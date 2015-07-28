FROM jhonatasmartins/geodjango

ADD ./docker-support /support
ADD ./server/requirements.txt /support/requirements.txt
VOLUME ["/app"]
RUN ["sh", "/support/setup.sh"]
EXPOSE 3000
