import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional

from app.dependencies.auth import get_current_user

from app.schemas.email import EmailSchema
from app.database import get_async_db
from app.settings import (
    FROM_EMAIL,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_USERNAME,
)

router = APIRouter(prefix="/email", tags=["E-Mail"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]

email_cc = ['mahendran@trustingroup.in' , 'benzimen@trustingroup.in']

darft_subject = "Draft test report for conformation"
darft_msg = """
Dear Sir/Madam,
 
Greetings from Trustin Analytical Solutions…!!
 
Please find the attached draft report for your review and conformation, kindly confirm to proceed further.


"""
subject = "Final test report"
message = """
Dear Sir/Madam,

Greetings from Trustin Analytical Solutions…!!

Please find the attached signed copy of test report for your reference.
"""
html_message = """
<html>
<body>
   <p style="color:"red";"}>Note: Kindly respond within three days, otherwise this report will be considered as the final.<p>

</body>
</html>
"""

def send_email(email: EmailSchema):
    try:
        msg = MIMEMultipart()
        msg["From"] = FROM_EMAIL
        msg["To"] = email.email
        msg["Cc"] = ','.join(email_cc)

        if email.email_type == "DRAFT":
            msg["Subject"] = darft_subject
            msg.attach(MIMEText(darft_msg, "plain"))
            msg.attach(MIMEText(html_message, "html"))
        else:
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "plain"))

        if email.attachment:
            pdf_blob = base64.b64decode(email.attachment)
            part = MIMEApplication(pdf_blob, Name=email.filename)
            part["Content-Disposition"] = f'attachment; filename="{email.filename}"'
            msg.attach(part)
        
        recipients = [email.email] + (email_cc if email_cc else [])


        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg, from_addr=FROM_EMAIL, to_addrs=recipients,)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/", status_code=status.HTTP_200_OK)
async def send_email_endpoint(email: EmailSchema, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email, email)
    return {"message": "Email has been sent in the background."}
