# https://chatgpt.com/c/6820fff4-a0c8-800c-a62c-cb439fe9d552
from uuid import uuid4
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
from datetime import datetime

class Video(Model):
    __keyspace__ = 'your_keyspace_name'

    video_id     = columns.UUID(primary_key=True, default=uuid4)
    user_id      = columns.UUID(index=True)

    title        = columns.Text()
    description  = columns.Text()

    s3_key       = columns.Text()
    gcs_key      = columns.Text()
    filename     = columns.Text()
    video_file   = columns.Text()
    thumbnail    = columns.Text()
    sprites      = columns.Text()

    created_at   = columns.DateTime(default=datetime.utcnow)
