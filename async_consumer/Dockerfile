FROM guldan_base:latest

ADD . /guldan_async
RUN pip install -r /guldan_async/requirements.txt
WORKDIR /guldan_async

ENTRYPOINT ["python", "/guldan_async/async_consumer.py"]

