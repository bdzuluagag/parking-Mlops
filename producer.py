import time
import json
import random
import datetime
from google.cloud import pubsub_v1

PROJECT_ID = "pure-heuristic-471315-i8"
TOPIC_ID = "parking-raw"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

# Tres parqueaderos simulados con diferente capacidad
PARKINGS = [
    {"parking_id": "P1", "capacity": 100},
    {"parking_id": "P2", "capacity": 120},
    {"parking_id": "P3", "capacity": 80},
]

def make_message(parking):
    """Genera un mensaje JSON con timestamp y disponibilidad simulada."""
    timestamp = datetime.datetime.now(datetime.UTC).isoformat()
    msg = {
        "timestamp": timestamp,
        "parking_id": parking["parking_id"],
        "available_spots": max(0, min(parking["capacity"],
            parking.get("available", parking["capacity"]) + random.randint(-3, 3)))
    }
    parking["available"] = msg["available_spots"]
    return json.dumps(msg).encode("utf-8")

def main():
    print("📡 Enviando mensajes a Pub/Sub cada 5 segundos. CTRL+C para detener.")
    while True:
        for p in PARKINGS:
            data = make_message(p)
            future = publisher.publish(topic_path, data=data)
            print("Publicado:", future.result())
        time.sleep(5)

if __name__ == "__main__":
    main()
