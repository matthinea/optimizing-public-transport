"""Defines trends calculations for stations"""
import logging

import faust


logger = logging.getLogger(__name__)


# Faust will ingest records from Kafka in this format
class Station(faust.Record):
    stop_id: int
    direction_id: str
    stop_name: str
    station_name: str
    station_descriptive_name: str
    station_id: int
    order: int
    red: bool
    blue: bool
    green: bool


# Faust will produce records to Kafka in this format
class TransformedStation(faust.Record):
    station_id: int
    station_name: str
    order: int
    line: str


# (DONE)TODO: Define a Faust Stream that ingests data from the Kafka Connect stations topic and
#   places it into a new topic with only the necessary information.
app = faust.App("stations-stream", broker="kafka://localhost:9092", store="memory://")
# (DONE)TODO: Define the input Kafka Topic. Hint: What topic did Kafka Connect output to?
topic = app.topic("cta.status_dashboard.stations", key_type=str, value_type=Station)
# (DONE)TODO: Define the output Kafka Topic
out_topic = app.topic("cta.status_dashboard.stations.gold", partitions=1)
# (DONE)TODO: Define a Faust Table
table = app.Table(
   "processed_stations",
   default=str,
   partitions=1,
   changelog_topic=out_topic,
)

# (DONE)TODO: Using Faust, transform input `Station` records into `TransformedStation` records. Note that
# "line" is the color of the station. So if the `Station` record has the field `red` set to true,
# then you would set the `line` of the `TransformedStation` record to the string `"red"`


@app.agent(topic)
async def process_stream(stream):
    """Transform 'Station' records into 'TransformedStation' records."""
    async for station in stream:
        if station.red:
            line = 'red'
        elif station.blue:
            line = 'blue'
        elif station.green:
            line = 'green'

        transformed_station = TransformedStation(
            station_id=station.station_id,
            station_name=station.station_name,
            order=station.order,
            line=line
        )

        table[station.station_id] = transformed_station

if __name__ == "__main__":
    app.main()
