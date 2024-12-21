from confluent_kafka import Consumer, KafkaException
import json
from notifier_template import send_email_template
from admin_kafka.topic_creation import bootstrap_servers
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

consumer_config = {
    'bootstrap.servers': ','.join(bootstrap_servers),
    'group.id': 'alert_notifier_group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False #disabilita l'auto-commit degli offset
}

consumer = Consumer(consumer_config)
consumer.subscribe(['to-notifier'])

# dizionario  per evitare email ridondanti
mail_cache = {}
"""
  Struttura:
  {
      'email_utente': {
          'value': <int>,
          'condition': <string ('HIGH'/'LOW')>,
          'ticker': <string>
      }
  }
"""
def is_cache_outdated(email, value_ticker, threshold_type, ticker):
    """
    Controlla se i dati correnti differiscono da quelli precedentemente inviati.
    Se coincidono, torna False (non inviamo la mail), altrimenti True.
    """
    if email in mail_cache:
        old_value = mail_cache[email]['value']
        old_condition = mail_cache[email]['condition']
        old_ticker = mail_cache[email]['ticker']

        # Converto l'attuale valore a int per evitare invii ripetuti per piccole differenze decimali
        current_value = int(value_ticker)
        current_condition = threshold_type.lower()

        logger.info(f"Confronto cache: email={email}, "
                    f"old_ticker={old_ticker}, new_ticker={ticker}, "
                    f"old_value={old_value}, new_value={current_value}, "
                    f"old_condition={old_condition}, new_condition={current_condition}")

        if current_value == old_value and current_condition == old_condition and old_ticker == ticker:
            return False
    return True

def save_into_cache(email, value_ticker, threshold_type, ticker):
    """
    Salva le informazioni correnti nella cache per evitare invii duplicati successivi.
    """
    if email not in mail_cache:
        mail_cache[email] = {}
    mail_cache[email]['value'] = int(value_ticker)
    mail_cache[email]['condition'] = threshold_type.lower()
    mail_cache[email]['ticker'] = ticker

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error(f"Errore: {msg.error()}")
            continue

        data = json.loads(msg.value().decode('utf-8'))
        email = data['email']
        ticker = data['ticker']
        threshold_value = data['threshold_value']
        threshold_type = data['threshold_type']
        value_ticker = data['value_ticker']

        # Controllo cache per evitare email duplicate
        if is_cache_outdated(email, value_ticker, threshold_type, ticker):
            send_email_template(email, ticker, threshold_value, threshold_type, value_ticker)
            logger.info(f"Email inviata a {email} per ticker {ticker}, soglia {threshold_type}")
            
            save_into_cache(email, value_ticker, threshold_type, ticker)
        else:
            logger.info(f"Email non inviata (valori invariati) per {email}, ticker {ticker}, soglia {threshold_type}")

        consumer.commit(asynchronous=False)

except KeyboardInterrupt:
    logger.info("Chiusura....")
finally:
    consumer.close()