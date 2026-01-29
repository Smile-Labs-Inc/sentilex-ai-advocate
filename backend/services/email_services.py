import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Email Configuration
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "smtp")  # smtp, sendgrid, ses
EMAIL_FROM = os.getenv("EMAIL_FROM", "noreply@sentilex.lk")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Sentilex AI Advocate")

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_TLS = os.getenv("SMTP_TLS", "true").lower() == "true"

# Frontend URLs
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


class EmailService:
    """Email service for sending transactional emails"""
    
    def __init__(self):
        self.enabled = EMAIL_ENABLED
        self.provider = EMAIL_PROVIDER
    
    def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email using configured provider"""
        
        if not self.enabled:
            logger.info(f"Email sending disabled. Would send to {to_email}: {subject}")
            return True
        
        try:
            if self.provider == "smtp":
                return self._send_smtp(to_email, subject, html_content, text_content)
            elif self.provider == "sendgrid":
                return self._send_sendgrid(to_email, subject, html_content)
            elif self.provider == "ses":
                return self._send_ses(to_email, subject, html_content)
            else:
                logger.error(f"Unknown email provider: {self.provider}")
                return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _send_smtp(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send email via SMTP"""
        
        if not SMTP_USER or not SMTP_PASSWORD:
            logger.error("SMTP credentials not configured")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{EMAIL_FROM_NAME} <{EMAIL_FROM}>"
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_content:
            part1 = MIMEText(text_content, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_content, 'html')
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            if SMTP_TLS:
                server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
    
    def _send_sendgrid(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via SendGrid"""
        # TODO: Implement SendGrid integration
        logger.warning("SendGrid integration not implemented yet")
        return False
    
    def _send_ses(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via AWS SES"""
        # TODO: Implement AWS SES integration
        logger.warning("AWS SES integration not implemented yet")
        return False

# Email Templates
def get_verification_email_html(verification_url: str, user_name: str) -> str:
    """Generate HTML for email verification"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">Sentilex AI Advocate</h1>
            <p style="color: white; margin: 10px 0 0 0;">Legal Justice Platform</p>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #667eea; margin-top: 0;">Verify Your Email Address</h2>
            
            <p>Dear {user_name},</p>
            
            <p>Thank you for registering with Sentilex AI Advocate. To complete your registration and start using our platform, please verify your email address.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; 
                          padding: 15px 40px; 
                          text-decoration: none; 
                          border-radius: 5px; 
                          display: inline-block;
                          font-weight: bold;">
                    Verify Email Address
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                If the button above doesn't work, copy and paste this link into your browser:<br>
                <a href="{verification_url}" style="color: #667eea; word-break: break-all;">{verification_url}</a>
            </p>
            
            <p style="color: #666; font-size: 14px; margin-top: 30px;">
                This verification link will expire in 24 hours for security reasons.
            </p>
            
            <p style="color: #666; font-size: 14px;">
                If you didn't create this account, please ignore this email.
            </p>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; text-align: center;">
                Sentilex AI Advocate - Bridging Trauma to Justice<br>
                This is an automated email, please do not reply.
            </p>
        </div>
    </body>
    </html>
    """


def get_password_reset_email_html(reset_url: str, user_name: str) -> str:
    """Generate HTML for password reset"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">Sentilex AI Advocate</h1>
            <p style="color: white; margin: 10px 0 0 0;">Password Reset Request</p>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #667eea; margin-top: 0;">Reset Your Password</h2>
            
            <p>Dear {user_name},</p>
            
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; 
                          padding: 15px 40px; 
                          text-decoration: none; 
                          border-radius: 5px; 
                          display: inline-block;
                          font-weight: bold;">
                    Reset Password
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                If the button above doesn't work, copy and paste this link into your browser:<br>
                <a href="{reset_url}" style="color: #667eea; word-break: break-all;">{reset_url}</a>
            </p>
            
            <div style="background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong style="color: #856404;">⚠️ Security Notice:</strong>
                <p style="color: #856404; margin: 5px 0 0 0; font-size: 14px;">
                    This password reset link will expire in 1 hour. If you didn't request this reset, please ignore this email and your password will remain unchanged.
                </p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; text-align: center;">
                Sentilex AI Advocate - Bridging Trauma to Justice<br>
                This is an automated email, please do not reply.
            </p>
        </div>
    </body>
    </html>
    """


def get_password_changed_email_html(user_name: str, ip_address: str, timestamp: str) -> str:
    """Generate HTML for password change notification"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">Sentilex AI Advocate</h1>
            <p style="color: white; margin: 10px 0 0 0;">Security Alert</p>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #667eea; margin-top: 0;">Password Changed Successfully</h2>
            
            <p>Dear {user_name},</p>
            
            <p>This is to confirm that your password was successfully changed.</p>
            
            <div style="background: #e8f4f8; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <p style="margin: 0; font-size: 14px;"><strong>Change Details:</strong></p>
                <p style="margin: 5px 0 0 0; font-size: 14px;">
                    <strong>Time:</strong> {timestamp}<br>
                    <strong>IP Address:</strong> {ip_address}
                </p>
            </div>
            
            <div style="background: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong style="color: #721c24;">🔒 Didn't make this change?</strong>
                <p style="color: #721c24; margin: 5px 0 0 0; font-size: 14px;">
                    If you didn't authorize this password change, please contact our support team immediately at support@sentilex.lk
                </p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; text-align: center;">
                Sentilex AI Advocate - Bridging Trauma to Justice<br>
                This is an automated email, please do not reply.
            </p>
        </div>
    </body>
    </html>
    """


def get_welcome_email_html(user_name: str) -> str:
    """Generate HTML for welcome email after verification"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">🎉 Welcome to Sentilex!</h1>
        </div>
        
        <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
            <h2 style="color: #667eea; margin-top: 0;">Your Account is Ready</h2>
            
            <p>Dear {user_name},</p>
            
            <p>Welcome to Sentilex AI Advocate! Your email has been verified and your account is now active.</p>
            
            <h3 style="color: #667eea;">What You Can Do Now:</h3>
            
            <ul style="padding-left: 20px;">
                <li style="margin-bottom: 10px;">📝 <strong>Report Incidents:</strong> File complaints with AI-powered legal support</li>
                <li style="margin-bottom: 10px;">⚖️ <strong>Legal Guidance:</strong> Get instant legal advice in Sinhala, Tamil, or English</li>
                <li style="margin-bottom: 10px;">👨‍⚖️ <strong>Find Lawyers:</strong> Connect with verified legal professionals</li>
                <li style="margin-bottom: 10px;">📚 <strong>Legal Knowledge:</strong> Access Sri Lankan law resources</li>
                <li style="margin-bottom: 10px;">🔒 <strong>Secure Evidence:</strong> Store documents with blockchain verification</li>
            </ul>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{FRONTEND_URL}/dashboard" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; 
                          padding: 15px 40px; 
                          text-decoration: none; 
                          border-radius: 5px; 
                          display: inline-block;
                          font-weight: bold;">
                    Go to Dashboard
                </a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; text-align: center;">
                Sentilex AI Advocate - Bridging Trauma to Justice<br>
                Need help? Email us at support@sentilex.lk
            </p>
        </div>
    </body>
    </html>
    """


# Helper functions for sending specific emails
email_service = EmailService()

def send_verification_email(email: str, token: str, user_name: str) -> bool:
    """Send email verification email"""
    verification_url = f"{FRONTEND_URL}/verify-email?token={token}"
    html_content = get_verification_email_html(verification_url, user_name)
    
    return email_service.send_email(
        to_email=email,
        subject="Verify Your Sentilex Account",
        html_content=html_content
    )


def send_password_reset_email(email: str, token: str, user_name: str) -> bool:
    """Send password reset email"""
    reset_url = f"{FRONTEND_URL}/reset-password?token={token}"
    html_content = get_password_reset_email_html(reset_url, user_name)
    
    return email_service.send_email(
        to_email=email,
        subject="Reset Your Sentilex Password",
        html_content=html_content
    )


def send_password_changed_email(
    email: str, 
    user_name: str, 
    ip_address: str,
    timestamp: str
) -> bool:
    """Send password change notification"""
    html_content = get_password_changed_email_html(user_name, ip_address, timestamp)
    
    return email_service.send_email(
        to_email=email,
        subject="Your Sentilex Password Was Changed",
        html_content=html_content
    )


def send_welcome_email(email: str, user_name: str) -> bool:
    """Send welcome email after verification"""
    html_content = get_welcome_email_html(user_name)
    
    return email_service.send_email(
        to_email=email,
        subject="Welcome to Sentilex AI Advocate! 🎉",
        html_content=html_content
    )