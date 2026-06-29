import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email using SendGrid"""
    if not SENDGRID_API_KEY:
        print("[email_service] SENDGRID_API_KEY not set")
        return False
    
    try:
        mail = Mail(
            from_email=Email("noreply@monikacafe.com", "Monika G Cafe"),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=body
        )
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)
        
        print(f"[email_service] Email sent to {to_email}: {response.status_code}")
        return response.status_code == 202
    except Exception as e:
        print(f"[email_service] Failed to send email: {e}")
        return False

def send_otp_email(to_email: str, otp_code: str) -> bool:
    """Send OTP email"""
    subject = "Your Monika G Cafe Login Code"
    body = f"""
Your login code is: {otp_code}

This code will expire in 5 minutes.
Do not share this code with anyone.

— Monika G Cafe
"""
    return send_email(to_email, subject, body)

def send_order_confirmation_email(to_email: str, order_id: int, total: float) -> bool:
    """Send order confirmation email"""
    subject = "Order Confirmation - Monika G Cafe"
    body = f"""
Your order has been placed!

Order ID: {order_id}
Total: ₹{total}

Thank you for your order!

— Monika G Cafe
"""
    return send_email(to_email, subject, body)