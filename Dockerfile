FROM jhonatasmartins/geodjango

ADD ./docker-support /support
VOLUME ["/app"]
RUN ["sh", "/support/setup.sh"]
EXPOSE 3000
