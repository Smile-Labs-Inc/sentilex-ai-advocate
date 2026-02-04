import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, html_content: str):
    """
    Send an email using SMTP settings from config.
    """
    try:
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            logger.warning("SMTP credentials not set. Email not sent.")
            logger.info(f"Would have sent email to {to_email} with subject: {subject}")
            return

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
        message["To"] = to_email

        # Attach HTML content
        part = MIMEText(html_content, "html")
        message.attach(part)

        # Connect to server
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, message.as_string())
            
        logger.info(f"Email sent successfully to {to_email}")

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        # Don't raise the exception to avoid crashing the request
        # In production, you might want to use a background task for emails


def send_verification_email(email: str, token: str, user_name: str):
    """Send account verification email"""
    subject = "Verify your SentiLex Account"
    
    # Get frontend URL from environment variable
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5174")
    verify_url = f"{frontend_url}/verify-email?token={token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Hello {user_name},</h2>
            <p>Welcome to SentiLex AI Advocate.</p>
            <p>Please verify your email address by clicking the link below:</p>
            <p><a href="{verify_url}">Verify Email</a></p>
            <p>This link will expire in 24 hours.</p>
            <br>
            <p>If you did not create an account, please ignore this email.</p>
        </body>
    </html>
    """
    
    send_email(email, subject, html_content)


def send_password_reset_email(email: str, token: str, user_name: str):
    """Send password reset email"""
    subject = "Reset your Password - SentiLex"
    
    reset_url = f"http://localhost:3000/reset-password?token={token}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Hello {user_name},</h2>
            <p>We received a request to reset your password.</p>
            <p>Click the link below to choose a new password:</p>
            <p><a href="{reset_url}">Reset Password</a></p>
            <p>This link will expire in 1 hour.</p>
            <br>
            <p>If you did not request a password reset, please ignore this email.</p>
        </body>
    </html>
    """
    
    send_email(email, subject, html_content)


def send_password_changed_email(email: str, user_name: str, ip_address: str, timestamp: str):
    """Send notification that password was changed"""
    subject = "Security Alert: Password Changed"
    
    html_content = f"""
    <html>
        <body>
            <h2>Hello {user_name},</h2>
            <p>Your password was successfully changed.</p>
            <p><strong>Time:</strong> {timestamp}</p>
            <p><strong>IP Address:</strong> {ip_address}</p>
            <br>
            <p>If verify this was you, no further action is needed.</p>
            <p>If you did NOT change your password, please contact support immediately.</p>
        </body>
    </html>
    """
    
    send_email(email, subject, html_content)


def send_welcome_email(email: str, user_name: str):
    """Send welcome email after verification"""
    subject = "Welcome to SentiLex AI Advocate!"
    
    html_content = f"""
    <html>
        <body>
            <h2>Welcome {user_name}!</h2>
            <p>Your email has been verified.</p>
            <p>You can now log in to your account and access all features.</p>
            <p><a href="http://localhost:3000/login">Go to Login</a></p>
        </body>
    </html>
    """
    
    send_email(email, subject, html_content)
