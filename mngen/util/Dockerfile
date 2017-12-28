FROM ubuntu
MAINTAINER Tomek Osiński <osinstom@gmail.com>

RUN apt-get update && apt-get install --no-install-recommends \
	python \
	python-dev

RUN pip --no-cache-dir install \
	Flask \
	flask_cors \
	lxml

EXPOSE 8181

CMD ["python mngen_api.py", "--allow-root"]
