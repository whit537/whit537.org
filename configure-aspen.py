import tree
import datetime
import re


website.hooks.startup.register(tree.startup)

def render_published(published):
    if re.match('^.*-\d\d:\d\d$', published) is not None:
        published = published[:-6]
    out = datetime.datetime.strptime(published, '%Y-%m-%dT%H:%M:%S.%f')
    out = out.strftime('%B %d, %Y')
    out = out.replace(' 0', ' ')
    return out

def add_stuff(request):
    request.context['render_published'] = render_published

website.hooks.inbound_early.register(add_stuff)
