import yfinance as yf
import time
from common.database import SessionLocal
from common.models import FinancialData, User
from circuit_breaker import CircuitBreaker
from confluent_kafka import Producer 

def delivery_report(err, msg):
    if err is not None:
        print(f"Errore nell'invio del messaggio: {err}")
    else:
        print(f"Messaggio inviato al topic {msg.topic()} partition [{msg.partition()}] offset [{msg.offset()}]")

def get_stock_price(ticker):
    data = yf.Ticker(ticker)
    hist = data.history(period="1d")
    if not hist.empty:
        return float(hist['Close'].iloc[0])
    else:
        raise ValueError(f"Nessun dato trovato per il ticker: {ticker}")

def main():
    
    #devo configurare il producer kafka 
    producer_config = {
         'bootstrap.servers': 'kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092',  # List of Kafka brokers
         'acks': 'all',  # Ensure all in-sync replicas acknowledge the message
         'max.in.flight.requests.per.connection': 1,  # Ensure ordering of messages
         'batch.size': 500,  # Maximum size of a batch in bytes
         'retries': 3  # Number of retries for failed messages
    }
    producer = Producer(producer_config)
    topic1 = 'to-alert-system'
    circuit_breaker = CircuitBreaker()
    while True:
        print("Avvio ciclo di raccolta dati")
        with SessionLocal() as session:
            tickers = session.query(User.ticker).distinct()
            tickers = [t[0] for t in tickers]
            for ticker in tickers:
                try:
                    price = circuit_breaker.call(get_stock_price, ticker)
                    price = float(price)
                    financial_data = FinancialData(
                        ticker=ticker,
                        value=price
                    )
                    session.add(financial_data)
                    session.commit()
                    print(f"Dato salvato per ticker {ticker}: {price}")
                except Exception as e:
                    print(f"Errore nel recupero dei dati per ticker {ticker}: {e}")
                    
                    
        #ho finito la raccolta dati, mando un mess tramite kafka
        message_update = "Update dei dati completato"
        producer.produce('to-alert-system', key='update', value=message_update.encode('utf-8'), callback=delivery_report)
        producer.flush()
       
        print("Ciclo di raccolta dati completato, attesa 3 minuti")
        time.sleep(180)

if __name__ == '__main__':
    main()
