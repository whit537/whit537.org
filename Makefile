env/lib/python2.7/site-packages/wsgiref: vendor/pypi/wsgiref
	./env/bin/pip install --no-index --find-links=./vendor/ -r requirements.txt

vendor/pypi/wsgiref: env
	./env/bin/pip install --download=./vendor/ -r requirements.txt

env:
	python2.7 ./vendor/bootstrap/virtualenv.py \
				--prompt="[whit537.org] " \
				--extra-search-dir=./vendor/bootstrap/ \
				./env/

clean:
	rm -rf env

run: env
	PATH=./env/bin:${PATH} ./run_dammit local.env web 
