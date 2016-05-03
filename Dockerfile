# docker build -t telminov/sms-service .

FROM g10k/filebeat
MAINTAINER telminov <telminov@soft-way.biz>

EXPOSE 8080

# directory for sqlite3 database
VOLUME /data/

# django settings
VOLUME /conf/

# django static-files
VOLUME /static/

# django logs
VOLUME /logs/

RUN apt-get update && \
    apt-get install -y \
                    vim \
                    supervisor

RUN mkdir /var/log/sms-service

# copy source
COPY . /opt/sms-service
WORKDIR /opt/sms-service

RUN pip3 install -r requirements.txt
RUN cp project/local_settings.sample.py project/local_settings.py

COPY supervisor/prod.conf /etc/supervisor/conf.d/sms-service.conf

CMD test "$(ls /conf/local_settings.py)" || cp project/local_settings.py /conf/local_settings.py; \
    test "$(ls /conf/filebeat.yml)" || cp /etc/filebeat/filebeat.yml /conf/filebeat.yml; \
    rm project/local_settings.py; ln -s /conf/local_settings.py project/local_settings.py; \
    rm /etc/filebeat/filebeat.yml; ln -s /conf/filebeat.yml /etc/filebeat/filebeat.yml; \
    rm -rf static; ln -s /static static; \
    service filebeat start; \
    python3 ./manage.py migrate; \
    python3 ./manage.py collectstatic --noinput; \
    /usr/bin/supervisord