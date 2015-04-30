#!/usr/bin/env python
"""Code to manage sensitive data, and the data.
"""
from __future__ import print_function

import cmd
import os
import pickle
import bcrypt
from cryptography.fernet import Fernet


class Vault(Fernet):
    """A simple database of dictionaries, with encrypted persistence.
    """

    def __init__(self, secret, filepath=os.path.join(os.path.dirname(__file__), 'vault.db')):
        Fernet.__init__(self, secret)
        self.filepath = filepath
        if not os.path.isfile(self.filepath):
            self.dump({})

    def load(self):
        encrypted = open(self.filepath).read()
        clear = self.decrypt(encrypted)
        return pickle.loads(clear)

    def dump(self, entities):
        clear = pickle.dumps(entities)
        encrypted = self.encrypt(clear)
        open(self.filepath, 'w+').write(encrypted)

    def list(self):
        return list(sorted(self.load().keys()))

    def upsert(self, code, **kw):
        entities = self.load()
        if code not in entities:
            entities[code] = {}
        entities[code].update(kw)
        self.dump(entities)

    def remove(self, code, key=None):
        entities = self.load()
        if code in entities:
            if key is None:
                del entities[code]
            else:
                if key in entities[code]:
                    del entities[code][key]
            self.dump(entities)


class VaultCmd(cmd.Cmd):

    def __init__(self, secret, salt, initial_cwe):
        cmd.Cmd.__init__(self)
        self.vault = Vault(secret)
        self.salt = salt
        self.cwe = initial_cwe  # cwe == current working entity (think cwd)
        self.update_prompt()

    def update_prompt(self):
        self.prompt = "vault|\x1b[32;1m{}\x1b[0m> ".format(self.cwe)

    def do_EOF(self, line):
        raise KeyboardInterrupt

    def do_quit(self, line):
        raise SystemExit
    do_exit = do_q = do_quit


    def do_l(self, line):
        "List key/values for current working entity."
        entities = self.vault.load()
        entity = entities.get(self.cwe)
        if entity:
            one, two = 0, 0
            kv = [('code', self.cwe)] + sorted(entity.items())
            for k,v in kv:
                one = max(one, len(k))
                for line in v.splitlines():
                    two = max(two, len(line))
            for k,v in kv:
                for line in v.splitlines():
                    print(("\x1b[34;1m{:%d}\x1b[0m " % one).format(k), end='')
                    print(("\x1b[36;1m{:%d}\x1b[0m" % two).format(line))
                    k = ''  # don't show key after first line


    def do_ls(self, line):
        "List available entities."
        for code in self.vault.list():
            print("\x1b[36;1m{}\x1b[0m".format(code))

    def complete_ls(self, text, line, begidx, endidx):
        return [n for n in self.vault.list() if n.startswith(text)]


    def do_ce(self, code):
        "Change current working entity."
        self.cwe = code
        self.update_prompt()

    complete_ce = complete_ls


    def do_set(self, line, salt=None):
        "Set a key/value pair for the current working entity."
        try:
            key, value = line.split(None, 1)
            value = value.decode('string_escape')  # allow user to enter newlines, etc.
        except ValueError:
            pass
        else:
            if salt:
                value = bcrypt.hashpw(value, salt)
            self.vault.upsert(self.cwe, **{key: value})
    do_s = do_set

    def complete_set(self, text, line, begidx, endidx):
        entities = self.vault.load()
        if self.cwe in entities:
            return [n for n in entities[self.cwe].keys() if n.startswith(text)]


    def do_seth(self, line):
        "Set a key/hashed value for the current working entity."
        return self.do_set(line, salt=self.salt)

    complete_seth = complete_set


    def do_rm(self, key):
        "Remove an entity key."
        if key.strip():
            self.vault.remove(self.cwe, key=key)
    do_r = do_rm

    complete_r = complete_rm = complete_set


    def do_remove_entity(self):
        "Remove an entire entity."
        self.vault.remove(self.cwe)
    # no tab-completion; make it hard!


def main(secret, salt, initial_cwe):
    try:
        VaultCmd(secret, salt, initial_cwe).cmdloop()
    except KeyboardInterrupt:
        print()


if __name__ == '__main__':
    secret = os.environ['VAULT_SECRET']
    salt = os.environ['VAULT_SALT']
    initial_cwe = os.environ['VAULT_INITIAL_CWE']
    main(secret, salt, initial_cwe)
