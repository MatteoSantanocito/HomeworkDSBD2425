import smtplib
from email.mime.text import MIMEText

def send_email_template(to_email, ticker, threshold_value, threshold_type,value_ticker):
    subject = f"Notifica Ticker {ticker}"
    if(threshold_type == 'HIGH'):
       body = f"Caro Utente, il valore di {ticker}: ({value_ticker}) ha superato la soglia {threshold_type}: {threshold_value}"
    elif(threshold_type == 'LOW'):
        body = f"Caro Utente, il valore di {ticker}: ({value_ticker}) è sceso sotto la soglia {threshold_type}: {threshold_value}"
    else:
        body = "Condizione di alert non riconosciuta."

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = "mattsantanocito@gmail.com"
    msg['To'] = to_email

    with smtplib.SMTP('smtp.gmail.com', 587) as s:
        s.starttls()
        s.login("mattsant625@gmail.com", "dtjfhrmvygbvezgt") 
        s.send_message(msg)
    print(f"Email inviata a {to_email} per ticker {ticker}, soglia {threshold_type}")