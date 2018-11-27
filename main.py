#!/usr/bin/env python3
from pymongo import MongoClient
import os
import pika
import json
import logging
from rabbit import Rabbit


MONGO_URL = os.getenv('MONGO_URL', 'localhost')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DB = os.getenv('MONGO_DB', 'my_db')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'my_collection')
mongoClient = MongoClient(f'mongodb://{MONGO_URL}', MONGO_PORT)
db = mongoClient[MONGO_DB]
collection = db[MONGO_COLLECTION]

LOG = logging
LOG.basicConfig(
    level=LOG.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def update_video_like(data):
    video_id = data.get('video_id')
    like = data.get('like')
    uid = data.get('uid')

    update_like_db = {}
    if like:
        update_like_db = {'$addToSet': {'likes': uid} }
    else:
        update_like_db = {'$pull': {'likes': uid} }

    collection.find_one_and_update(
        {'video_id': video_id},
        update_like_db
    )

    return video_id


def callback(ch, method, properties, body):
    # update data in mongo db
    LOG.info("Message Recieved")
    data = json.loads(body)
    video_id = update_video_like(data)

    LOG.info(f'Like status of video, {video_id}, is updated')


if __name__ == '__main__':
    rabbit = Rabbit('like')
    rabbit.consume(callback)
    LOG.info(' [*] Waiting for Job.')
    
    rabbit.start_consuming()