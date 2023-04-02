import sys
import logging
import json
from math import sin, cos
from time import sleep
from kafka import KafkaProducer

logger = logging.getLogger("algorithm_service")

def create_producer(servers) -> KafkaProducer:
    assert isinstance(servers, list)

    try:
        return KafkaProducer(bootstrap_servers=servers)
    except Exception as e:
        logger.warning("Fail state in create_producer")
        logger.error(e)
        return None

def send_position_message(producer: KafkaProducer, x, y, z):
    
    data = json.dumps({
        "x": x,
        "y": y,
        "z": z,
    })
    producer.send("BALL_POSITION", value=data.encode('utf-8'))
    # make ready to send
    producer.flush()
    return

if __name__ == "__main__":
    # FORMAT = '%(asctime)s %(clientip)-15s %(user)-8s %(message)s'
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.DEBUG)
    producer = None
    err_count = 0

    while producer is None:
        producer = create_producer([
            "kafka:29092",
        ])

        if producer is None:
            logger.error(f"Kafka producer cannot be created. Error count at {err_count+1}")
            sleep(1)
            err_count += 1
        else:
            err_count = 0

        if err_count == 5:
            logger.info(f"Error count reached maximum ({err_count}) exiting program.")
            sys.exit(1)

    count = 0
    max_val = 360
    rad = 5
    
    while True:
        x = rad * cos(count % max_val)
        y = rad * sin(count % max_val)

        send_position_message(producer, x, y, 0)

        sleep(1)
        count += 1
