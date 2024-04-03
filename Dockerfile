FROM ubuntu:jammy

RUN apt-get -y update && apt-get -y upgrade
RUN apt-get -y install python3 python3-pip

WORKDIR /app
COPY --chown=1001 . .

RUN pip install -r requirements.txt

USER 1001
CMD ["python3", "main.py"]