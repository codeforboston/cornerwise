FROM python:3.6

ADD ./docker-support /support
ADD ./server /app
ADD ./client /client
ADD ./data /data
RUN ["sh", "/support/setup.sh"]
WORKDIR "/app"
EXPOSE 3000
