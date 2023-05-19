FROM python:3.8.12-bullseye
ENV PYTHONPATH "${PYTHONPATH}:/code/tpt_service"

RUN apt-get update && apt-get install nginx supervisor -y

# Version to use
ARG TESLA_CE_TPT_LIB_VERSION

# Define the TeSLA CE package to install
ARG TESLA_CE_TPT_LIB_PACKAGE="tesla-ce-provider-pt-tpt-lib==$TESLA_CE_TPT_LIB_VERSION"


#RUN apk update && apk add postgresql-dev gcc g++ make python3-dev musl-dev libxml2-dev \
#libxslt-dev build-base linux-headers pcre-dev nginx xmlsec-dev jpeg-dev zlib-dev freetype-dev \
#lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev supervisor

#RUN apk add --no-cache bash git py2-pip gcc g++ make libffi-dev linux-headers libxml2-dev
# xmlsec-dev jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev openssl
# python-dev postgresql-client postgresql-dev nginx \
#	&& pip2 install --upgrade pip gunicorn

RUN mkdir -p /code/tpt_service
COPY tpt_service/requirements.txt /code/tpt_service/requirements.txt

#COPY tpt_service/tpt-1.0-py2.py3-none-any.whl /code/tpt_service/tpt-1.0-py2.py3-none-any.whl

WORKDIR /code/tpt_service
RUN pip install -r requirements.txt
RUN pip install --no-cache-dir $TESLA_CE_TPT_LIB_PACKAGE

COPY tpt_service /code/tpt_service
RUN cp /code/tpt_service/tpt_prod.ini /code/tpt_service/tpt.ini

COPY docker/worker.sh /code
RUN chmod a+x /code/worker.sh

#RUN rm /etc/nginx/conf.d/default.conf
RUN rm -r /root/.cache

COPY docker/nginx.conf /etc/nginx/
COPY docker/flask-site-nginx.conf /etc/nginx/conf.d/flask-site-nginx.conf

RUN mkdir -p /etc/uwsgi
RUN mkdir -p /var/log/uswgi
COPY docker/uwsgi.ini /etc/uwsgi/uwsgi.ini

RUN mkdir -p /etc/supervisor
COPY docker/supervisord.conf /etc/supervisor/supervisord.conf

WORKDIR /code
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]

#HEALTHCHECK
