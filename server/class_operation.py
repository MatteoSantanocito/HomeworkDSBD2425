import logging
import re
from common.database import SessionLocal
from common import models

logger = logging.getLogger(__name__)

def is_valid_email(email):
    regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(regex, email) is not None

class RegisterUserCommand:
    def __init__(self, email, ticker, request_id, high_value, low_value):
        self.email = email
        self.ticker = ticker
        self.request_id = request_id
        self.high_value = high_value if high_value != 0.0 else None
        self.low_value = low_value if low_value != 0.0 else None

    def execute(self):
        if not is_valid_email(self.email):
            logger.info(f"Formato email non valido: {self.email}")
            return "Email non valida.", False, "Email non valida.", None

        if not self.ticker:
            logger.info("Ticker non può essere vuoto.")
            return "Ticker non può essere vuoto.", False, "Ticker non può essere vuoto.", None

        if self.high_value is not None and self.low_value is not None and self.high_value <= self.low_value:
            err_message = "ATTENZIONE hai inserito un valore di high_value minore del valore di low_value."
            return err_message, False, err_message, None

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=self.email).first()
            if user:
                message = "Utente già registrato."
                logger.info(f"Utente già registrato: {self.email}")
            else:
                new_user = models.User(email=self.email, ticker=self.ticker, high_value=self.high_value, low_value=self.low_value)
                session.add(new_user)
                session.commit()
                message = "Registrazione effettuata con successo."
                logger.info(f"Nuovo utente registrato: {self.email}")

            return message, True, None, None
        except Exception as e:
            logger.error(f"Errore in RegisterUser: {e}")
            return "Errore interno.", False, f'Errore: {str(e)}', "INTERNAL"
        finally:
            session.close()


class UpdateUserCommand:
    def __init__(self, email, ticker, request_id, high_value, low_value):
        self.email = email
        self.ticker = ticker
        self.request_id = request_id
        self.high_value = high_value if high_value != 0.0 else None
        self.low_value = low_value if low_value != 0.0 else None

    def execute(self):
        if not is_valid_email(self.email):
            logger.info(f"Formato email non valido: {self.email}")
            return "Email non valida.", False, "Email non valida.", None

        if not self.ticker:
            logger.info("Ticker non può essere vuoto.")
            return "Ticker non può essere vuoto.", False, "Ticker non può essere vuoto.", None

        if self.high_value is not None and self.low_value is not None and self.high_value <= self.low_value:
            err_message = "ATTENZIONE hai inserito un valore di high_value minore del valore di low_value."
            return err_message, False, err_message, None

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=self.email).first()
            if user:
                if self.ticker:
                    user.ticker = self.ticker
                if self.high_value is not None:
                    user.high_value = self.high_value
                if self.low_value is not None:
                    user.low_value = self.low_value
                session.commit()
                message = "Ticker aggiornato con successo."
                logger.info(f"Ticker aggiornato per: {self.email}")
                return message, True, None, None
            else:
                message = "Utente non trovato."
                logger.info(f"Utente non trovato: {self.email}")
                return message, False, "Utente non trovato.", "NOT_FOUND"
        except Exception as e:
            logger.error(f"Errore in UpdateUser: {e}")
            return "Errore nell'aggiornamento utente.", False, f'Errore: {str(e)}', "INTERNAL"
        finally:
            session.close()


class DeleteUserCommand:
    def __init__(self, email, request_id):
        self.email = email
        self.request_id = request_id

    def execute(self):
        if not is_valid_email(self.email):
            logger.info(f"Formato email non valido: {self.email}")
            return "Email non valida.", False, "Email non valida.", None

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=self.email).first()
            if user:
                session.delete(user)
                session.commit()
                message = "Account cancellato con successo."
                logger.info(f"Account cancellato per: {self.email}")
                return message, True, None, None
            else:
                message = "Utente non trovato."
                logger.info(f"Utente non trovato: {self.email}")
                return message, False, "Utente non trovato.", "NOT_FOUND"
        except Exception as e:
            logger.error(f"Errore in DeleteUser: {e}")
            return "Errore interno.", False, f'Errore: {str(e)}', "INTERNAL"
        finally:
            session.close()


class LoginUserCommand:
    def __init__(self, email, request_id):
        self.email = email
        self.request_id = request_id

    def execute(self):
        if not is_valid_email(self.email):
            logger.info(f"Formato email non valido: {self.email}")
            return "Email non valida.", False, "Email non valida.", None

        session = SessionLocal()
        try:
            user = session.query(models.User).filter_by(email=self.email).first()
            if user:
                message = "Login effettuato con successo."
                logger.info(f"Utente loggato: {self.email}")
                return message, True, None, None
            else:
                message = "Utente non trovato."
                logger.info(f"Utente non trovato: {self.email}")
                return message, False, "Utente non trovato.", "NOT_FOUND"
        except Exception as e:
            logger.error(f"Errore in LoginUser: {e}")
            return "Errore interno.", False, f'Errore: {str(e)}', "INTERNAL"
        finally:
            session.close()