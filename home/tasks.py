from bucket import bucket
from A.celery_conf import celery_app

# can be async?
def all_bucket_objects_task():
    result = bucket.get_objects()
    return result

@celery_app.task
def delete_object_task(key):
    bucket.delete_object(key)

@celery_app.task
def download_object_task(key):
    bucket.download_object(key)
