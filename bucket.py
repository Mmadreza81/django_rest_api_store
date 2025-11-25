import boto3
from django.conf import settings
from decouple import config


class Bucket:
    """CDN Bucket manager

    init method creates connection.

    NOTE:
        none of these methods are async. use public interface in tasks.py module instead.
    """

    def __init__(self):
        session = boto3.session.Session()
        self.conn = session.client(
            service_name=config('SERVICE_NAME'),
            aws_access_key_id=config('ACCESS_KEY'),
            aws_secret_access_key=config('STORAGE_SECRET_KEY'),
            endpoint_url=config('ENDPOINT_URL'),
        )

    def get_objects(self):
        result = self.conn.list_objects_v2(Bucket=config('BUCKET_NAME'))
        if result['KeyCount']:
            return result['Contents']
        else:
            return None

    def delete_object(self, key):
        self.conn.delete_object(Bucket=config('BUCKET_NAME'), Key=key)
        return True

    def download_object(self, key):
        with open(settings.AWS_LOCAL_STORAGE + key, 'wb') as f:
            self.conn.download_fileobj(config('BUCKET_NAME'), key, f)


bucket = Bucket()
