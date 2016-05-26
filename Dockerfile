FROM python:3.5.1

ADD ./docker-support /support
ADD ./data/shapefiles /shapefiles
ADD ./server /app
ADD ./client /client
ADD ./data /data
RUN ["sh", "/support/setup.sh"]
EXPOSE 3000
