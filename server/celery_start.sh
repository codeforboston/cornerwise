cd $(dirname "${BASH_SOURCE[0]}")

export C_FORCE_ROOT=1

if [ "$APP_MODE" = "production" ]; then
    # Only run tasks automatically in production:
    celery -A cornerwise beat --detach
else
    celery_opts=" --loglevel=INFO --autoreload"
fi

celery -A cornerwise worker $celery_opts
