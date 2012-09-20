   
env:
	python2.7 ./vendor/virtualenv-1.7.1.2.py \
				--unzip-setuptools \
				--prompt="[blag] " \
				--never-download \
				--extra-search-dir=./vendor/ \
				--distribute \
				./env/
	./env/bin/pip install -r requirements.txt

clean:
	rm -rf env

run: env
	MONGO="mongodb://localhost/blag" \
		sudo -E ./env/bin/aspen \
		--www_root=www/ \
		--project_root=../ \
		--show_tracebacks=yes \
		--changes_reload=yes \
		--network_address=:80

