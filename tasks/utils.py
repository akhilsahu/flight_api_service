from celery import Celery
import os
def make_celery(app):
    # This pulls the 'CELERY_CONFIG' we defined above
    conf = app.config.get("CELERY_CONFIG", {})
    # Default to environment variable if app.config is empty
    default_redis = os.environ.get("REDIS_URL", "redis://redis:6379/0")
    celery = Celery(
        app.import_name,
        broker=conf.get("broker_url",default_redis),
        backend=conf.get("result_backend",default_redis)
    )
    celery.conf.update(conf)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            # This ensures that whenever a task runs, 
            # it has access to app.config and database connections
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery