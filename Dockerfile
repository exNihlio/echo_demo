FROM ubuntu:18.04

RUN apt-get update \ 
    && apt-get -y install python3 python3-pip \
    && pip3 install gunicorn bottle \
    && mkdir -p /app/python

COPY app.py /app/python/
COPY entrypoint.sh /app/python/
COPY .env_vars /app/python/

EXPOSE 8080

WORKDIR /app/python

RUN chmod 755 entrypoint.sh

#CMD ["source", "/app/python/.env_vars", "&&", "gunicorn", "-b", "${HOST_IP}:${HOST_PORT}", "-w", "${WORKERS}", "app:app"]
ENTRYPOINT ["bash", "entrypoint.sh"]