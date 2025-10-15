"""
dataflow_pipeline.py
Pipeline de streaming con Apache Beam que:
1. Lee mensajes JSON desde Pub/Sub.
2. Parsea el contenido.
3. Inserta registros en BigQuery.
"""

import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

class ParseJson(beam.DoFn):
    """Convierte los mensajes JSON en diccionarios compatibles con BigQuery."""
    def process(self, element):
        record = json.loads(element.decode("utf-8"))
        yield {
            "timestamp": record.get("timestamp"),
            "parking_id": record.get("parking_id"),
            "available_spots": record.get("available_spots")
        }

def run(argv=None):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--input_topic", required=True)
    parser.add_argument("--dataset_table", required=True)
    parser.add_argument("--temp_location", required=True)
    parser.add_argument("--region", required=True)
    args, pipeline_args = parser.parse_known_args(argv)

    options = PipelineOptions(
        project=args.project,
        temp_location=args.temp_location,
        region=args.region,
        streaming=True,
        runner="DataflowRunner"
    )
    p = beam.Pipeline(options=options)

    (
        p
        | "Leer de Pub/Sub" >> beam.io.ReadFromPubSub(topic=args.input_topic)
        | "Parsear JSON" >> beam.ParDo(ParseJson())
        | "Escribir en BigQuery" >> beam.io.WriteToBigQuery(
            args.dataset_table,
            schema="timestamp:TIMESTAMP, parking_id:STRING, available_spots:INTEGER",
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        )
    )

    p.run().wait_until_finish()

if __name__ == "__main__":
    run()
