FROM python:3.6

ADD ./docker-support /support
WORKDIR "/app"
EXPOSE 3000
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal
RUN apt-get update && \
    apt-get install -y libgdal-dev binutils gdal-bin xpdf-utils && \
    pip3 install -r /support/requirements.txt

ADD ./server /app
ADD ./data /data

CMD bash /app/start.sh
