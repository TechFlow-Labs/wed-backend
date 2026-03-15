from fastapi_mail import FastMail, MessageSchema, MessageType
from email_service.conf import connection

async def send_status_email(to_email: str, vendor_name: str, event_date: str, new_status: str):
    
    # Set up the content based on the status
    if new_status == "ACCEPTED":
        subject = f"Good news! Your reservation with {vendor_name} is accepted"
        body = f"""
        <h3>Great news!</h3>
        <p><strong>{vendor_name}</strong> has officially accepted your reservation for <strong>{event_date}</strong>.</p>
        <p>Log in to your Wedding Plan dashboard to view the details or message the vendor.</p>
        """
    elif new_status == "REJECTED":
        subject = f"Update on your reservation with {vendor_name}"
        body = f"""
        <h3>Reservation Update</h3>
        <p>Unfortunately, <strong>{vendor_name}</strong> is unable to accommodate your reservation for <strong>{event_date}</strong>.</p>
        <p>Don't worry! There are plenty of other amazing partners on the platform.</p>
        """
    else:
        return

    # Construct the message
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],  # fastapi-mail expects a list of recipients
        body=body,
        subtype=MessageType.html
    )


    fm = FastMail(connection)
    await fm.send_message(message)