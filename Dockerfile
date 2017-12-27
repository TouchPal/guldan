FROM guldan_base:latest

ADD . /webapp
ENV HOME /webapp
WORKDIR /webapp

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "guldan_start.py"]

