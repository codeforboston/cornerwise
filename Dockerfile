FROM python:alpine

WORKDIR "/app"
EXPOSE 3000
CMD bash /app/start.sh

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal
ADD ./docker-support /support
RUN apk add --no-cache \
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing\
    --repository http://dl-cdn.alpinelinux.org/alpine/edge/community\
    bash binutils build-base git inotify-tools libcrypto1.0 libxml2 libxslt  \
    poppler-utils \
    freetype-dev lcms2-dev libjpeg-turbo libpng-dev libwebp-dev libzip-dev tcl-dev tk-dev \
    gdal libpq postgresql-dev && \
    pip3 install -r /support/requirements.txt

# RUN apt-get update && \
#     apt-get install -y libgdal-dev binutils gdal-bin xpdf-utils inotify-tools && \
#     pip3 install -r /support/requirements.txt

ADD ./server /app
