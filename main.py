#!/usr/bin/env python3
from pymongo import MongoClient
import os
import pika
import json
import logging


MONGO_URL = os.getenv('MONGO_URL', 'localhost')
MONGO_PORT = os.getenv('MONGO_PORT', 27017)
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

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()


channel.queue_declare(queue='like')


def update_vid_like(data):
    vid_id = data['vid_id']
    is_unlike = data['is_unlike']
    incr = 1
    if is_unlike:
        incr = -1

    collection.find_one_and_update(
        {'vid_id': vid_id},
        {'$inc': {'vid_like': incr}}
    )

    return vid_id


def callback(ch, method, properties, body):
    # update data in mongo db
    print("Message Recieved")
    data = json.loads(body)
    vid_id = update_vid_like(data)

    LOG.info(f'Like status of video, {vid_id}, is updated')


channel.basic_consume(callback,
                      queue='like',
                      no_ack=True)


LOG.info(' [*] Waiting for Job.')
channel.start_consuming()
