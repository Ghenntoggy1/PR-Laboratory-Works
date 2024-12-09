import smtplib
import telnetlib
from email.mime.message import MIMEMessage
from email.mime.text import MIMEText

from dotenv import load_dotenv
from fastapi import FastAPI, status, Response
from pydantic import BaseModel
import os
# IF RUN FROM PYCHARM
load_dotenv(".env")
SMTP_SERVER_PORT = int(os.getenv("SMTP_SERVER_PORT"))
SMTP_GMAIL_PORT = int(os.getenv("SMTP_GMAIL_PORT"))
SMTP_SERVER_HOST = os.getenv("SMTP_HOST_NAME", "smtp.gmail.com")
app = FastAPI()


class EmailRequest(BaseModel):
    sender_email: str
    sender_password: str
    receiver_emails: list[str]
    subject: str
    body: str

@app.post("/send_email")
def send_email(request: EmailRequest):
    if len(request.receiver_emails) == 0 or request.subject == "" or request.body == "":
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Empty fields are not allowed")
    try:
        email_message = MIMEText(request.body)
        email_message["Subject"] = request.subject
        email_message["From"] = request.sender_email
        email_message["To"] = ", ".join(request.receiver_emails)
        smtp_server = smtplib.SMTP("smtp.gmail.com", SMTP_GMAIL_PORT)
        smtp_server.starttls()
        print(request.sender_email, request.sender_password)
        smtp_server.login(request.sender_email, request.sender_password)
        message = f"Subject: {request.subject}\n\n{request.body}"
        smtp_server.sendmail(request.sender_email, request.receiver_emails, message)

        return Response(status_code=status.HTTP_200_OK, content="Email sent successfully")
    except Exception as e:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(e))

def send_smtp_telnet(host: str, port: int, sender_email: str, sender_password: str, receiver_email: str, subject: str, body: str):
    # Establish Telnet connection to the SMTP server
    with telnetlib.Telnet(host, port) as tn:
        tn.read_until(b"220")
        tn.write(b"HELO localhost\r\n")
        tn.read_until(b"250")

        # Authentication (if required)
        tn.write(b"AUTH LOGIN\r\n")
        tn.read_until(b"334")
        tn.write(f"{sender_email.encode('ascii').hex()}\r\n".encode())
        tn.read_until(b"334")
        tn.write(f"{sender_password.encode('ascii').hex()}\r\n".encode())
        tn.read_until(b"235")

        # Send MAIL FROM command
        tn.write(f"MAIL FROM:<{sender_email}>\r\n".encode())
        tn.read_until(b"250")

        # Send RCPT TO command
        tn.write(f"RCPT TO:<{receiver_email}>\r\n".encode())
        tn.read_until(b"250")

        # Send DATA command
        tn.write(b"DATA\r\n")
        tn.read_until(b"354")
        tn.write(f"Subject: {subject}\r\n\r\n{body}\r\n.\r\n".encode())
        tn.read_until(b"250")

        # Quit the session
        tn.write(b"QUIT\r\n")
        tn.read_until(b"221")


@app.post("/send_email_telnet")
def send_email_telnet(request: EmailRequest):
    if not request.receiver_email or not request.subject or not request.body:
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Empty fields are not allowed")
    try:
        send_smtp_telnet(
            host=SMTP_SERVER_HOST,
            port=SMTP_GMAIL_PORT,
            sender_email=request.sender_email,
            sender_password=request.sender_password,
            receiver_email=request.receiver_email,
            subject=request.subject,
            body=request.body
        )
        return Response(status_code=status.HTTP_200_OK, content="Email sent successfully via Telnet")
    except Exception as e:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=f"Error sending email: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SMTP_SERVER_PORT)