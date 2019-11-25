FROM python:3.8

COPY . /

RUN pip install -r requirements.txt

ENV DEBUG 'False'
ENV SECRET_KEY 'key'
ENV REGION 'gcp-us-east1'
ENV DB_URI 'connection_string'
ENV API_KEY 'API_key'

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "server:app"]
