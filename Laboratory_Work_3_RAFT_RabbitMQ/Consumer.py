import time
from ftplib import FTP
from threading import Thread

import pika
import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

RABBIT_MQ_USERNAME = os.getenv("RABBIT_MQ_USERNAME")
RABBIT_MQ_PASSWORD = os.getenv("RABBIT_MQ_PASSWORD")
FTP_USERNAME = os.getenv("FTP_USERNAME")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT"))
FTP_DATA_DIRECTORY = os.getenv("FTP_DATA_DIRECTORY")
FTP_CONTAINER_NAME = os.getenv("FTP_CONTAINER_NAME")
RABBIT_MQ_CONTAINER_NAME = os.getenv("RABBIT_MQ_CONTAINER_NAME")


http_leader_host = ""
http_leader_port = 0

def udp_handler():
    pass

def connect_to_rabbit_mq() -> tuple:
    credentials = pika.PlainCredentials(RABBIT_MQ_USERNAME, RABBIT_MQ_PASSWORD)
    parameters = pika.ConnectionParameters(RABBIT_MQ_CONTAINER_NAME, 5672, '/', credentials)
    print(parameters)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    """
    Declares an exchange for the producer to publish messages to, since producer should never send messages directly to the 
    queue. In this case, the exchange is of type direct, which means that the message will be sent to the queue with the
    specified routing key.
    """
    channel.exchange_declare(exchange='phones_json', exchange_type='direct')

    """
    Creates an empty queue, that takes a random name and is deleted once consumer is closed. This is called Temporary Queue.
    """
    result = channel.queue_declare(queue='', exclusive=True)

    """
    Get the name of the created queue
    """
    queue_name = result.method.queue

    """
    Bind the queue to the exchange. This is done in order to tell the exchange to send messages to this queue. 
    The routing_key is the key that the exchange will use to route messages to this queue.
    """
    channel.queue_bind(exchange='phones_json', queue=queue_name, routing_key='phones_json')
    return channel, queue_name

def callback(channel, method, properties, body):
    print(f" [x] {body}")
    channel.basic_ack(delivery_tag=method.delivery_tag)
    # Simulate delay
    time.sleep(5)

def consume_from_rabbit_mq():
    channel, queue_name = connect_to_rabbit_mq()
    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    channel.start_consuming()

def consume_file_from_ftp():
    output_file_path = "ftp_data/phones_ftp.json"
    while True:
        print("WAITING FOR FILE")
        time.sleep(10)
        print("READY TO CONSUME FILE")
        if not os.path.exists("ftp_data"):
            os.makedirs("ftp_data")
        ftp = FTP(host=FTP_CONTAINER_NAME)
        ftp.login(user=FTP_USERNAME,
                  passwd=FTP_PASSWORD)
        if FTP_DATA_DIRECTORY not in ftp.nlst():
            print("Directory does not exist")
            continue
        ftp.cwd(FTP_DATA_DIRECTORY)
        if "phones.json" not in ftp.nlst():
            print("File does not exist")
            continue
        localfile = open(output_file_path, 'wb')
        ftp.retrbinary(f"RETR phones.json", localfile.write, 1024)
        ftp.quit()
        localfile.close()
        print("File downloaded")
        with open(output_file_path, "rb") as file:
            content = file.read()
            content_str = content.decode("utf-8")
            print(content_str)

if __name__ == '__main__':
    consumer_rabbit_mq = Thread(target=consume_from_rabbit_mq)
    consumer_ftp = Thread(target=consume_file_from_ftp)

    consumer_rabbit_mq.start()
    consumer_ftp.start()

    consumer_rabbit_mq.join()
    consumer_ftp.join()