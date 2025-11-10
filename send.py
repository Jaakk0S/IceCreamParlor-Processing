#!/usr/bin/env python
import pika, sys

outputQueue = sys.argv[1]
body = sys.argv[2]

connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials(username='producer', password='producer')))
channel = connection.channel()

channel.basic_publish(exchange='', routing_key=outputQueue, body=body)
print(f" [x] Sent {body}")
connection.close()
