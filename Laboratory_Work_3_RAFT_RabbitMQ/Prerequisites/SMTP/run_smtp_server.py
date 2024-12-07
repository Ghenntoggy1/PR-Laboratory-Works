import smtplib
from dotenv import load_dotenv
from fastapi import FastAPI, status, Response
from pydantic import BaseModel
import os
# IF RUN FROM PYCHARM
load_dotenv(".env")
SMTP_SERVER_PORT = int(os.getenv("SMTP_SERVER_PORT"))
SMTP_GMAIL_PORT = int(os.getenv("SMTP_GMAIL_PORT"))
app = FastAPI()


class EmailRequest(BaseModel):
    sender_email: str
    sender_password: str
    receiver_email: str
    subject: str
    body: str

@app.post("/send_email")
def send_email(request: EmailRequest):
    if request.receiver_email == "" or request.subject == "" or request.body == "":
        return Response(status_code=status.HTTP_400_BAD_REQUEST, content="Empty fields are not allowed")
    # try:
    smtp_server = smtplib.SMTP("smtp.gmail.com", SMTP_GMAIL_PORT)
    smtp_server.starttls()
    print(request.sender_email, request.sender_password)
    smtp_server.login(request.sender_email, request.sender_password)
    message = f"Subject: {request.subject}\n\n{request.body}"
    smtp_server.sendmail(request.sender_email, request.receiver_email, message)

    return Response(status_code=status.HTTP_200_OK, content="Email sent successfully")
    # except Exception as e:
    #     return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=SMTP_SERVER_PORT)