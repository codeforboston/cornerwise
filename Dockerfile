FROM python:3.4.3

ADD ./docker-support /support
ADD ./data/shapefiles /shapefiles
ADD ./server /app
ADD ./client /client
ADD ./data /data
RUN ["sh", "/support/setup.sh"]
EXPOSE 3000
