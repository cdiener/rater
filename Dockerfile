FROM debian:jessie

RUN apt-get update -y \
    && apt-get install -y nginx ca-certificates wget python3 python3-dev bzip2 \
    python3-pip supervisor build-essential libopenblas-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PATH /opt/conda/bin:$PATH

COPY . /app
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/sites-available/default
COPY supervisor.conf /etc/supervisor/conf.d/

# send local logs to docker logs
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

RUN pip3 install -r /app/requirements.txt && rm -rf /tmp/*

RUN cd /app && rm data/*.db && python3 -c "from app import init_db; init_db()" \
    && chown -hR www-data:www-data /app

EXPOSE 80 443

CMD ["/usr/bin/supervisord"]
