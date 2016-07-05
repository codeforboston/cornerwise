FROM python:3.5.1

ADD ./docker-support /support
ADD ./server /app
ADD ./client /client
ADD ./data /data
RUN ["sh", "/support/setup.sh"]
WORKDIR "/app"
EXPOSE 3000
