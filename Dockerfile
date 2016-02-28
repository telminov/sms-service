# docker build -t telminov/sms-service .

FROM telminov/ubuntu-14.04-python-3.5
MAINTAINER telminov <telminov@soft-way.biz>

EXPOSE 8080

# directory for sqlite3 database
VOLUME /data/

# django settings
VOLUME /conf/

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
    rm project/local_settings.py; \
    ln -s /conf/local_settings.py project/local_settings.py; \
    python3 ./manage.py migrate; \
    /usr/bin/supervisord