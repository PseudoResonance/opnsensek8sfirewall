FROM python:alpine

COPY --from=root requirements.txt /tmp

RUN mkdir -p /opt && \
	cd /opt && \
	cp /tmp/requirements.txt ./ && \
	pip3 install -r requirements.txt

COPY --from=root ./ /opt/

WORKDIR /opt

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/usr/local/bin/python3", "/opt/run.py"]
