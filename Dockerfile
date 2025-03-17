FROM ghcr.io/maxotta/kiv-dsa-vagrant-base-docker:latest

RUN yum -q -y install epel-release && \
    yum -q -y install python3

COPY src /app/src

CMD ["python3", "-u", "/app/src/main.py"]