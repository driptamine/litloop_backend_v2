# https://chatgpt.com/c/6820fff4-a0c8-800c-a62c-cb439fe9d552
from uuid import uuid4
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import columns
from datetime import datetime

class Photo(Model):
    __keyspace__ = 'your_keyspace_name'

    photo_id    = columns.UUID(primary_key=True, default=uuid4)
    user_id     = columns.UUID(index=True)

    title       = columns.Text()
    s3_key      = columns.Text()
    gcs_key     = columns.Text()
    filename    = columns.Text()
    photo_file  = columns.Text()

    created_at  = columns.DateTime(default=datetime.utcnow)
    friendly_token = columns.Text(index=True)

    like_user_ids       = columns.Set(columns.UUID)
    dislike_user_ids    = columns.Set(columns.UUID)
    view_user_ids       = columns.Set(columns.UUID)
    impression_user_ids = columns.Set(columns.UUID)


class PhotoAlbum(Model):
    __keyspace__ = 'your_keyspace_name'

    album_id       = columns.UUID(primary_key=True, default=uuid4)
    user_id        = columns.UUID(index=True)

    title          = columns.Text()
    description    = columns.Text()
    photo_ids      = columns.List(columns.UUID)
    friendly_token = columns.Text(index=True)
    created_at     = columns.DateTime(default=datetime.utcnow)


class PhotoAlbumItem(Model):
    __keyspace__ = 'your_keyspace_name'

    album_id   = columns.UUID(partition_key=True)
    ordering   = columns.Integer(primary_key=True)
    photo_id   = columns.UUID()
    action_date = columns.DateTime(default=datetime.utcnow)
