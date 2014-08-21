from celery import Celery




loghub_worker = Celery("loghub_worker", broker="amqp://loghub//",
                    backend= 'mongodb://loghub//',
                    include= ['loghub.modules.users','loghub.modules.alarms','loghub.modules.applications','loghub.modules.logs']
                    )

loghub_worker.conf.update(
    CELERY_DEFAULT_QUEUE='loghub',
    CELERY_DEFAULT_ROUTING_KEY='loghub',
    CELERY_DEFAULT_EXCHANGE='loghub',
    CELERY_TIMEZONE = 'UTC',
    CELERY_TASK_RESULT_EXPIRES = 60 * 36,
    CELERYD_CONCURRENCY = 4,
    CELERYD_PREFETCH_MULTIPLIER = 2,
    CELERYD_TASK_SOFT_TIME_LIMIT = 60 * 4,
    CELERYD_TASK_TIME_LIMIT = 60 * 5,

    )