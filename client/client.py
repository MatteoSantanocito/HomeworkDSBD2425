import grpc
import service_pb2 as service_pb2
import service_pb2_grpc
import uuid
import yfinance as yf
import logging
from time import sleep
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

session_email = None

def generate_request_id():
    return str(uuid.uuid4())

def ticker_verifier(ticker):
    #qui sfrutto una funzione che utilizza yf perfare il downlaod del ticker, mi torna utile per ottimizzare
    #le richieste di insert, evito alla base di inserire il ticker se non è valido
    #naturalmente ho gestito anche il caso in cui yfinance smetta di funzionare, evitando quindi l'inserimento di ticker
    
        dati = yf.download(ticker, period="1d", progress=False)
        if not dati.empty:
            logger.info(f"Il ticker '{ticker}' è valido.")
            return True
        else:
            logger.warning(f"Il ticker '{ticker}' non è valido.")
            return False
    

def send_request_with_retry(stub_method, request, max_retries=5, initial_delay=1, backoff_factor=2, jitter=0.1):
    attempts = 0
    delay = initial_delay
    while attempts < max_retries:
        # qui ho deciso di implementare un sistema con jitter per incrementare esponenzialmente l'attesa
        # è una mia implementazione già utilizzata in altre materie che permette una corretta gestione dell'attesa
        try:
            response = stub_method(request, timeout=5)  
            return response
        except grpc.RpcError as e:
            if e.code() in [grpc.StatusCode.DEADLINE_EXCEEDED, grpc.StatusCode.UNAVAILABLE, grpc.StatusCode.INTERNAL]:
                attempts += 1
                sleep_time = delay + random.uniform(0, jitter)
                logger.warning(f"Tentativo {attempts} di {max_retries} fallito ({e.code().name}). Riprovo dopo {sleep_time:.2f} secondi...")
                sleep(sleep_time) 
                delay *= backoff_factor  
            else:
                logger.error(f"Errore durante la richiesta: {e}")
                break
    logger.error("Impossibile contattare il server dopo diversi tentativi.")
    return None

def run():
    global session_email
    with grpc.insecure_channel('localhost:50051') as canale:
        stub = service_pb2_grpc.UserServiceStub(canale)
        while True:
            print("\n--- Menù di avvio ---")
            print("1. Login")
            print("2. Registrazione")
            print("3. Esci")
            scelta = input("Inserisci il numero dell'operazione desiderata: ")

            if scelta == '1':
                email = input("Inserisci la tua email: ").strip()
                if not email:
                    print("Email non può essere vuota.")
                    continue
                request_id = generate_request_id() 
                request = service_pb2.LoginUserRequest(email=email, request_id=request_id)
                response = send_request_with_retry(stub.LoginUser, request)
                if response:
                    if hasattr(response, 'success') and response.success:
                        print(response.message)
                        session_email = email
                        user_session(stub)
                    elif hasattr(response, 'message'):
                        print(response.message)
                    else:
                        print("Risposta del server inattesa.")
                else:
                    print("Errore durante il login.")
            elif scelta == '2':
                email = input("Inserisci l'email dell'utente: ").strip()
                if not email:
                    print("Email non può essere vuota.")
                    continue
                ticker = input("Inserisci il ticker di interesse: ").strip().upper()
                if not ticker:
                    print("Ticker non può essere vuoto.")
                    continue
                if ticker_verifier(ticker):
                    request_id = generate_request_id()
                    request = service_pb2.RegisterUserRequest(email=email, ticker=ticker, request_id=request_id)
                    response = send_request_with_retry(stub.RegisterUser, request)
                    if response:
                        print(response.message)
                        if "success" in response.message.lower():
                            session_email = email
                            user_session(stub)
                    else:
                        print("Errore durante la registrazione.")
                    
                else:
                    print("Ticker non valido. Registrazione annullata.")
            elif scelta == '3':
                print("Uscita dal programma... Alla prossima!")
                break
            else:
                print("Scelta non valida. Riprova.")

def user_session(stub):
    """
    Gestisce le operazioni utente dopo il login.
    """
    global session_email
    while session_email:
        print(f"\n--- BENVENUTO {session_email} ---")
        print("\nSeleziona un'operazione:")
        print("1. Aggiornamento Ticker")
        print("2. Cancellazione Account")
        print("3. Recupero dell'ultimo valore disponibile")
        print("4. Calcolo della media degli ultimi X valori")
        print("5. Logout")
        scelta = input("Inserisci il numero dell'operazione desiderata: ")

        if scelta == '1':
            ticker = input("Inserisci il nuovo ticker: ").strip().upper()
            if not ticker:
                print("Ticker non può essere vuoto.")
                continue
            if ticker_verifier(ticker):
                request_id = generate_request_id()
                request = service_pb2.UpdateUserRequest(
                    email=session_email,
                    ticker=ticker,
                    request_id=request_id
                )
                response = send_request_with_retry(stub.UpdateUser, request)
                if response:
                    print(response.message)
                else:
                    print("Errore durante l'aggiornamento del ticker.")
            else:
                print("Ticker non valido. Aggiornamento annullato.")
        elif scelta == '2':
            conferma = input("Sei sicuro di voler cancellare il tuo account? (s/n): ").strip().lower()
            if conferma == 's':
                request_id = generate_request_id()
                request = service_pb2.DeleteUserRequest(email=session_email, request_id=request_id)
                response = send_request_with_retry(stub.DeleteUser, request)
                if response:
                    print(response.message)
                    if "cancellato" in response.message.lower():
                        session_email = None
                        print("Sei stato disconnesso.")
                else:
                    print("Errore durante la cancellazione dell'account.")
            else:
                print("Cancellazione annullata.")
        elif scelta == '3':
            email = session_email
            request = service_pb2.GetLatestValueRequest(email=email)
            response = send_request_with_retry(stub.GetLatestValue, request)
            if response:
                if hasattr(response, 'ticker') and response.ticker:
                    print(f"Ultimo valore per {response.ticker}: {response.value} (Timestamp: {response.timestamp})")
                else:
                    print("Nessun dato disponibile per l'utente specificato.")
            else:
                print("Nessun dato disponibile per l'utente specificato. Attendi 3 minuti.")
        elif scelta == '4':
            count_input = input("Quanti valori vuoi considerare per la media? ").strip()
            if not count_input.isdigit() or int(count_input) <= 0:
                print("Per favore, inserisci un numero intero positivo valido.")
                continue
            count = int(count_input)
            request = service_pb2.GetAverageValueRequest(email=session_email, count=count)
            response = send_request_with_retry(stub.GetAverageValue, request)
            if response:
                if hasattr(response, 'ticker') and response.ticker:
                    print(f"Valore medio per {response.ticker}: {response.average_value}")
                else:
                    print("Nessun dato disponibile per l'utente specificato.")
            else:
                print("Errore durante il calcolo della media.")
        elif scelta == '5':
            print("Logout effettuato.")
            session_email = None
        else:
            print("Scelta non valida. Riprova.")

if __name__ == '__main__':
    run()