FROM debian:jessie

RUN apt-get update && apt-get install -y \
    nginx \
    python3 \
    python3-pip \
    supervisor

# Consider moving these 3 lines after pip install so that changes don't affect the cache.
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN rm /etc/nginx/sites-enabled/default
RUN ln -s /home/docker/code/lazyvore_nginx.conf /etc/nginx/sites-enabled/

# Add requirements.txt separately so that Docker can use it's cache effectively.
ADD ./requirements.txt /home/docker/code/
WORKDIR /home/docker/code/
RUN pip3 install --allow-external mysql-connector-python -r requirements.txt

ENV INI_PATH /home/docker/code/production.ini
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["/usr/bin/supervisord"]
EXPOSE 80 443

# run any addition pip install commands.
# Now add remaining files which will likely change frequently.
ADD . /home/docker/code/
RUN python3 setup.py install
