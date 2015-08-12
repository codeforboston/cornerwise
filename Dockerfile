FROM python:3.4.3

ADD ./docker-support /support
ADD ./data/shapefiles /shapefiles
VOLUME ["/app"]
RUN ["sh", "/support/setup.sh"]
EXPOSE 3000
