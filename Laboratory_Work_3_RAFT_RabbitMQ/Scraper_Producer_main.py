from threading import Thread
from dotenv import load_dotenv
import pika
import os
from ftplib import FTP

from Prerequisites.ScraperUtils.Phone import PhoneEntity
from Prerequisites.ScraperUtils.UrllibHTMLRequester import UrllibHTMLRequester
from Prerequisites.ScraperUtils.Scraper_utils import get_phones_html, get_phone_from_html, \
    process_phones
from Prerequisites.ScraperUtils.PhoneEntityProcessor import serialize_phone_JSON
from Prerequisites.ScraperUtils.Constants import Constants

load_dotenv(dotenv_path="../.env")

RABBIT_MQ_USERNAME = os.getenv("RABBIT_MQ_USERNAME")
RABBIT_MQ_PASSWORD = os.getenv("RABBIT_MQ_PASSWORD")
FTP_USERNAME = os.getenv("FTP_USERNAME")
FTP_PASSWORD = os.getenv("FTP_PASSWORD")
FTP_HOST = os.getenv("FTP_HOST")
FTP_PORT = int(os.getenv("FTP_PORT"))
FTP_DATA_DIRECTORY = os.getenv("FTP_DATA_DIRECTORY")

def connect_to_rabbit_mq():
    credentials = pika.PlainCredentials(RABBIT_MQ_USERNAME, RABBIT_MQ_PASSWORD)
    parameters = pika.ConnectionParameters('localhost', 5672, '/', credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    """
    Declares an exchange for the producer to publish messages to, since producer should never send messages directly to the 
    queue. In this case, the exchange is of type direct, which means that the message will be sent to the queue with the
    specified routing key.
    """
    channel.exchange_declare(exchange='phones_json', exchange_type='direct')
    return channel

def scrape_send_to_rabbit_mq():
    channel = connect_to_rabbit_mq()
    urllib_web_scraper: UrllibHTMLRequester = UrllibHTMLRequester(url=Constants.URL_WEBSITE_2)
    phones_html = get_phones_html(urllib_web_scraper)
    for phone_html in phones_html:
        phone: PhoneEntity = get_phone_from_html(urllib_web_scraper, phone_html)
        print(get_phone_from_html(urllib_web_scraper, phone_html))
        phone_json_serialized = serialize_phone_JSON(phone.to_dict())
        """
        Publish a message to the exchange with the specified routing key. The exchange will automatically route the
        message to the queue with the specified routing key.
        """
        channel.basic_publish(exchange='phones_json',
                              routing_key='phones_json',
                              body=phone_json_serialized)

    channel.close()

def scrape_send_to_ftp():
    urllib_web_scraper: UrllibHTMLRequester = UrllibHTMLRequester(url=Constants.URL_WEBSITE)
    phones_html = get_phones_html(urllib_web_scraper)
    phone_dicts = []
    for phone_html in phones_html:
        phone: PhoneEntity = get_phone_from_html(urllib_web_scraper, phone_html)
        phone_dicts.append(phone)
        # print(phone)
    processed_phones: list[PhoneEntity] = process_phones(min_price=400, max_price=600, new_currency="EUR", phones=phone_dicts).filtered_phones
    processed_phones_dicts: list[dict] = [phone_entity.to_dict() for phone_entity in processed_phones]
    phones_json = serialize_phone_JSON(processed_phones_dicts)
    output_file_path = "ftp_data/phones.json"
    if not os.path.exists("ftp_data"):
        os.makedirs("ftp_data")
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
    with open(output_file_path, "wb") as file:
        file.write(phones_json)

    upload_to_ftp(output_file_path)

def upload_to_ftp(file_path: str):
    ftp = FTP(host=FTP_HOST,
              user=FTP_USERNAME,
              passwd=FTP_PASSWORD)
    print("Current Directory:", ftp.dir())
    print("DATA:", ftp.nlst())
    if FTP_DATA_DIRECTORY not in ftp.nlst():
        ftp.mkd(FTP_DATA_DIRECTORY)
    ftp.cwd(FTP_DATA_DIRECTORY)
    with open(file_path, "rb") as file:
        ftp.storbinary(f"STOR {file_path.split('/')[-1]}", file)
    print("Current Directory:", ftp.dir())
    ftp.quit()

if __name__ == '__main__':
    rabbit_mq = Thread(target=scrape_send_to_rabbit_mq)
    ftp_server = Thread(target=scrape_send_to_ftp)

    rabbit_mq.start()
    ftp_server.start()

    rabbit_mq.join()
    ftp_server.join()
