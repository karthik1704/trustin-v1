import base64
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List, Optional

from app.dependencies.auth import get_current_user

from app.models.email import EmailStatus
from app.schemas.email import EmailSchema
from app.database import AsyncSessionFactory, get_async_db
from app.settings import (
    FROM_EMAIL,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
    SMTP_USERNAME,
)

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email", tags=["E-Mail"])

db_dep = Annotated[AsyncSession, Depends(get_async_db)]
user_dep = Annotated[dict, Depends(get_current_user)]

email_cc = ["mahendran@trustingroup.in", "benzimen@trustingroup.in"]

darft_subject = "Draft test report for conformation"
darft_msg = """
Dear Sir/Madam,
 
Greetings from Trustin Analytical Solutions…!!
 
Please find the attached draft report for your review and conformation, kindly confirm to proceed further.

Note: Kindly respond within three days, otherwise this report will be considered as the final.
"""
subject = "Final test report"
message = """
Dear Sir/Madam,

Greetings from Trustin Analytical Solutions…!!

Please find the attached signed copy of test report for your reference.
"""
html_message = """\
<html>
<body>
   <p>Dear Sir/Madam,</p>
   <p>Greetings from Trustin Analytical Solutions…!!</p>
   <p>Please find the attached draft report for your review and confirmation, kindly confirm to proceed further.</p>
   <p style="color:red;">Note: Kindly respond within three days, otherwise this report will be considered as the final.</p>
</body>
</html>
"""


async def send_email(email: EmailSchema, user: user_dep , db:AsyncSession = Depends(get_async_db)):
 
    # async with AsyncSessionFactory() as db:
    email_status = EmailStatus(
        recipient=email.email,
        subject=subject,
        sent=False,
        reason=None,
        sample_id=email.sample_id,
        sent_by=user.get("id"),
    )
    db.add(email_status)
    await db.commit()

    try:
        msg = EmailMessage()
        msg["From"] = FROM_EMAIL
        msg["To"] = email.email
        msg["Cc"] = ",".join(email_cc)

        if email.email_type == "DRAFT":
            msg["Subject"] = darft_subject
            msg.set_content(
                darft_msg,
            )
            msg.add_alternative(html_message, subtype="html")
            email_status.subject = darft_subject
        else:
            msg["Subject"] = subject
            msg.set_content(
                message,
            )
            email_status.subject = subject

        if email.attachment:
            pdf_blob = base64.b64decode(email.attachment)
            # Add the attachment to the EmailMessage
            msg.add_attachment(
                pdf_blob, maintype="application", subtype="pdf", filename= f"{email.filename}.pdf" if email.email_type != "DRAFT" else f"{email.filename}(Draft).pdf"
            )

        recipients = [email.email] + (email_cc if email_cc else [])

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:

            server.ehlo()
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)

            # Send the email
            server.send_message(
                msg,
                from_addr=FROM_EMAIL,
                to_addrs=recipients,
            )
            email_status.sent = True

    except smtplib.SMTPException as e:
        email_status.reason = f"Unexpected error: {str(e)}"
        print(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    except Exception as e:
        email_status.reason = f"Unexpected error: {str(e)}"
        print(f"Failed to send email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    finally:
        await db.commit()


@router.post("/", status_code=status.HTTP_200_OK)
async def send_email_endpoint(
    email: EmailSchema, background_tasks: BackgroundTasks, db: db_dep, user: user_dep
):
   
    background_tasks.add_task(send_email, email, user, db)
    return {"message": "Email has been sent in the background."}
