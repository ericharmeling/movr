FROM python:3.8

COPY . /

RUN pip install -r requirements.txt

ENV DB_HOST 'localhost'
ENV DB_PORT 26257
ENV DB_USER 'root'
ENV DB_URI 'cockroachdb://root@127.0.0.1:58827/movr'
ENV SECRET_KEY 'key'
ENV REGION 'us-east1'

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "server:app"]
