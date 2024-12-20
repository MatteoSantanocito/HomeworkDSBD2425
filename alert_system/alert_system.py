from confluent_kafka import Consumer, Producer, KafkaException
import os
from common.database import SessionLocal
from common.models import User
from sqlalchemy import text
import json
import logging
from admin_kafka.topic_creation import bootstrap_servers

logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger(__name__)

consumer_config = {
    'bootstrap.servers': ','.join(bootstrap_servers), 
    'group.id': 'alert_system_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
}

producer_config = {
    'bootstrap.servers': ','.join(bootstrap_servers), 
    'acks': 'all',  # Ensure all in-sync replicas acknowledge the message
    'linger.ms': 500, # Tempo massimo che il produttore aspetta prima di inviare i messaggi nel buffer
    'compression.type': 'gzip',  # Compressione dei messaggi per ridurre la larghezza di banda
    'max.in.flight.requests.per.connection': 1,  # Numero massimo di richieste inviate senza risposta
    'retries': 3,  # Numero di tentativi di invio in caso di errore
}

in_topic = 'to-alert-system'
out_topic = 'to-notifier'

consumer = Consumer(consumer_config)
producer = Producer(producer_config)

consumer.subscribe(['to-alert-system'])

def delivery_report(err, msg):
    if err is not None:
        logger.error(f"Errore nell'inviare messaggio a {out_topic}: {err}")
    else:
        logger.info(f"Messaggio inviato a to-notifier offset {msg.offset()}")

def threshold_verifier(user, value_ticker, high_value, low_value):
    """
    Verifica se il valore_ticker supera le soglie high_value o low_value e produce un messaggio 
    sul topic 'to-notifier' se necessario. 
    """
    if high_value is not None and value_ticker > high_value:
        alert = {
            "email": user.email, 
            "ticker": user.ticker, 
            "threshold_value": high_value, 
            "threshold_type": "HIGH", 
            "value_ticker": value_ticker
        }
        logger.info(f"Valore {value_ticker} > {high_value} per {user.email}, invio notifica HIGH.")
        producer.produce(out_topic, json.dumps(alert).encode('utf-8'), callback=delivery_report)
      
    if low_value is not None and value_ticker < low_value:
        alert = {
            "email": user.email, 
            "ticker": user.ticker,
            "threshold_value": low_value, 
            "threshold_type": "LOW",
            "value_ticker": value_ticker
        }
        logger.info(f"Valore {value_ticker} < {low_value} per {user.email}, invio notifica LOW.")
        producer.produce(out_topic, json.dumps(alert).encode('utf-8'), callback=delivery_report)


while True:
    try:
        msg = consumer.poll(1.0)
        if msg is None:
            continue

        if msg.error():
            logger.error(f"Errore nel consumare messaggio: {msg.error()}")
            continue

        
        if msg.key() and msg.key().decode('utf-8') == 'update':
            logger.info("Messaggio ricevuto da to-alert-system. Inizio scansione database...")

            with SessionLocal() as session:
                users = session.query(User).all()
                for user in users:
                    if user.ticker:
                        latest = session.execute(
                            text('SELECT value FROM financial_data WHERE ticker=:ticker ORDER BY timestamp DESC LIMIT 1'),
                            {"ticker": user.ticker}
                        ).fetchone()

                        if latest:
                            value_ticker = latest[0]
                            high_value = user.high_value
                            low_value = user.low_value

                            # Verifica soglie
                            threshold_verifier(user, value_ticker, high_value, low_value)

               
                producer.flush()
                session.commit()

        
        consumer.commit()
        logger.info("Offset committato con successo.")
    except KeyboardInterrupt:
        logger.info("Interruzione del programma da parte dell'utente.")
        break
    except Exception as e:
        logger.error(f"Errore durante l'esecuzione: {e}")
        break

consumer.close()