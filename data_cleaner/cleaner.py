import time
import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from common.database import SessionLocal, engine
from common.models import FinancialData, User
from common import models
from sqlalchemy.exc import OperationalError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_old_data():
    with SessionLocal() as session:
        try:
            logger.info("Inizio pulizia dei dati...")
            
            active_tickers = session.query(User.ticker).distinct().all()
            active_tickers = [t[0] for t in active_tickers if t[0]]
            logger.info(f"Ticker attivi: {active_tickers}")

            delete_inactive = session.query(FinancialData).filter(~FinancialData.ticker.in_(active_tickers))
            count_inactive = delete_inactive.count()
            if count_inactive > 0:
                delete_inactive.delete(synchronize_session=False)
                session.commit()
                logger.info(f"Eliminati {count_inactive} record di ticker non attivi.")
            else:
                logger.info("Nessun record di ticker non attivo da eliminare.")

            tickers = session.query(FinancialData.ticker).distinct().all()
            tickers = [t[0] for t in tickers]

            for ticker in tickers:
                total_records = session.query(FinancialData).filter_by(ticker=ticker).count()

                # Se ci sono più di 20 record, elimina i più vecchi
                # ho deciso di non eliminarli tutti, così posso mantenere qualche valore di riempimento della tabella
                if total_records > 20:
                    records_to_delete = total_records - 20

                    old_records = session.query(FinancialData.id)\
                        .filter_by(ticker=ticker)\
                        .order_by(FinancialData.timestamp.asc())\
                        .limit(records_to_delete)\
                        .all()

                    old_record_ids = [record.id for record in old_records]
                    session.query(FinancialData)\
                        .filter(FinancialData.id.in_(old_record_ids))\
                        .delete(synchronize_session=False)

                    session.commit()
                    logger.info(f"Eliminati {records_to_delete} vecchi record per il ticker {ticker}.")
                else:
                    logger.info(f"Nessun record da eliminare per il ticker {ticker}.")

            logger.info("Pulizia dei dati completata.")
        except Exception as e:
            session.rollback()
            logger.error(f"Errore durante la pulizia dei dati: {e}")
            raise

def main():
    while True:
        try:
            clean_old_data()
        except Exception as e:
            logger.error(f"Errore nel ciclo di pulizia: {e}")
        logger.info("Il processo si attiverà di nuovo tra 24 ore.")
        time.sleep(86400)

if __name__ == '__main__':
    main()