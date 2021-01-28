"""Defines core consumer functionality"""
import logging

import confluent_kafka
from confluent_kafka import Consumer
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError
from tornado import gen


logger = logging.getLogger(__name__)


class KafkaConsumer:
    """Defines the base kafka consumer class"""

    KAFKA_URL = 'localhost:9092'
    SCHEMA_REGISTRY_URL = 'http://localhost:8081'

    def __init__(
        self,
        topic_name_pattern,
        message_handler,
        is_avro=True,
        offset_earliest=False,
        sleep_secs=1.0,
        consume_timeout=0.1,
    ):
        """Creates a consumer object for asynchronous use"""
        self.topic_name_pattern = topic_name_pattern
        self.message_handler = message_handler
        self.sleep_secs = sleep_secs
        self.consume_timeout = consume_timeout
        self.offset_earliest = offset_earliest

        # (DONE)TODO: Configure the broker properties below. Make sure to reference the project README
        # and use the Host URL for Kafka and Schema Registry!
        self.broker_properties = {
            'bootstrap.servers': self.KAFKA_URL,
            'group.id': 'hinea-group-id'
        }

        # (DONE)TODO: Create the Consumer, using the appropriate type.
        if is_avro is True:
            self.broker_properties["schema.registry.url"] = "http://localhost:8081"
            self.consumer = AvroConsumer(self.broker_properties)
        else:
            self.consumer = Consumer(self.broker_properties)

        # (DONE)TODO: Configure the AvroConsumer and subscribe to the topics. Make sure to think about
        # how the `on_assign` callback should be invoked.
        self.consumer.subscribe([topic_name_pattern], on_assign=self.on_assign)

    def on_assign(self, consumer, partitions):
        """Callback for when topic assignment takes place"""
        # (DONE)TODO: If the topic is configured to use `offset_earliest` set the partition offset to
        # the beginning or earliest
        if self.offset_earliest:
            for partition in partitions:
                partition.offset = confluent_kafka.OFFSET_BEGINNING

        logger.info("partitions assigned for %s", self.topic_name_pattern)
        consumer.assign(partitions)

    async def consume(self):
        """Asynchronously consumes data from kafka topic"""
        while True:
            num_results = 1
            while num_results > 0:
                num_results = self._consume()
            await gen.sleep(self.sleep_secs)

    def _consume(self):
        """Polls for a message. Returns 1 if a message was received, 0 otherwise"""
        # (DONE)TODO: Poll Kafka for messages. Make sure to handle any errors or exceptions.
        try:
            message = self.consumer.poll()
            if message is None:
                return 0
            elif message.error() is None:
                self.message_handler(message)
                return 1
            else:
                raise message.error().code()
        except Exception as exc:
            logger.info("error polling consumer: %s", exc)

    def close(self):
        """Cleans up any open kafka consumers"""
        # (DONE)TODO: Cleanup the kafka consumer
        self.consumer.close()
