PY=pyenv/bin/python

scrape: pyenv/bin/python
	$(PY) scraper_accreditations.py

pyenv/bin/python:
	virtualenv pyenv
	pyenv/bin/pip install --upgrade pip
	pyenv/bin/pip install -r requirements.txt

clean:
	rm -rf pyenv
