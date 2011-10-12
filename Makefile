   
env:
	python2.7 virtualenv-1.6.4.py --distribute \
			                      --no-site-packages \
			                      --unzip-setuptools \
			                      --prompt="[blag] " \
			                      env/
	./env/bin/pip install -r requirements.txt

clean:
	rm -rf env

run: env
	MONGO="mongodb://localhost/blag" sudo -E ./env/bin/thrash ./env/bin/aspen -vDEBUG -a:80 www/
