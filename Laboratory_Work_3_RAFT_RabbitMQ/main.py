from threading import Thread
from dotenv import load_dotenv
import pika
import os

from Laboratory_Work_1_Scraper_HTTP_Requests.Phone import PhoneEntity
from Laboratory_Work_1_Scraper_HTTP_Requests.UrllibHTMLRequester import UrllibHTMLRequester
from Laboratory_Work_1_Scraper_HTTP_Requests.main import serialize_phone_JSON, get_phones_html, get_phone_from_html

from Laboratory_Work_3_RAFT_RabbitMQ import Consumer

load_dotenv(dotenv_path="../.env")

RABBIT_MQ_USERNAME = os.getenv("RABBIT_MQ_USERNAME")
RABBIT_MQ_PASSWORD = os.getenv("RABBIT_MQ_PASSWORD")
print(RABBIT_MQ_USERNAME)
print(RABBIT_MQ_PASSWORD)
credentials = pika.PlainCredentials(RABBIT_MQ_USERNAME, RABBIT_MQ_PASSWORD)
parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)

def scrape():
    urllib_web_scraper: UrllibHTMLRequester = UrllibHTMLRequester()

    phones_html = get_phones_html(urllib_web_scraper)

    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange='phones_json', exchange_type='direct')


    for phone_html in phones_html:
        phone: PhoneEntity = get_phone_from_html(urllib_web_scraper, phone_html)
        # print(get_phone_from_html(urllib_web_scraper, phone_html))
        phone_json_serialized = serialize_phone_JSON(phone.to_dict())
        channel.basic_publish(exchange='phones_json', routing_key='phones_json', body=phone_json_serialized)

    connection.close()

if __name__ == '__main__':
    rabbit_mq = Thread(target=scrape)
    consumer_rabbit_mq = Thread(target=Consumer.consume)

    rabbit_mq.start()
    consumer_rabbit_mq.start()

    rabbit_mq.join()
    consumer_rabbit_mq.join()
