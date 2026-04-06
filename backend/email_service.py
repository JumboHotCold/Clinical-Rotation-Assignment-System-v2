from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from both backend and root directories
backend_env = Path(__file__).parent / ".env"
root_env = Path(__file__).parent.parent / ".env"

if backend_env.exists():
    load_dotenv(backend_env)
    print(f"[ENV] Loaded .env from backend directory: {backend_env}")
elif root_env.exists():
    load_dotenv(root_env)
    print(f"[ENV] Loaded .env from root directory: {root_env}")
else:
    print("[ENV] No .env file found in backend or root directory")

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "noreply@clinicalrotation.com")

def send_student_welcome_email(student_email: str, student_name: str, default_password: str, student_id: str):
    """
    Send welcome email to newly created student account
    """
    if not SENDGRID_API_KEY:
        print("[WARNING] SENDGRID_API_KEY not set in .env file. Email not sent.")
        return False
    
    try:
        print(f"\n[EMAIL] Starting email process...")
        print(f"[EMAIL] Recipient: {student_email}")
        print(f"[EMAIL] Sender: {SENDER_EMAIL}")
        print(f"[EMAIL] API Key present: {bool(SENDGRID_API_KEY)}")
        print(f"[EMAIL] API Key (first 20 chars): {SENDGRID_API_KEY[:20]}...")
        
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        
        subject = "Welcome to Clinical Rotation Assignment System - Your Account Credentials"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                    <h2 style="color: #2c3e50;">Welcome to Clinical Rotation Assignment System</h2>
                    
                    <p>Hello <strong>{student_name}</strong>,</p>
                    
                    <p>Your account has been successfully created by the admin. Below are your login credentials:</p>
                    
                    <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0;">
                        <p><strong>Student ID (Username):</strong> {student_id}</p>
                        <p><strong>Default Password:</strong> <code style="background-color: #e8f4f8; padding: 2px 6px; border-radius: 3px;">{default_password}</code></p>
                    </div>
                    
                    <h3 style="color: #2c3e50;">Important Security Instructions:</h3>
                    <ol style="margin-left: 20px;">
                        <li>Log in using your Student ID and the default password provided above.</li>
                        <li><strong>Immediately change your password</strong> upon first login for security purposes.</li>
                        <li>Your new password should be strong and unique. Do not share it with anyone.</li>
                        <li>Keep your account credentials confidential.</li>
                    </ol>
                    
                    <h3 style="color: #2c3e50;">Next Steps:</h3>
                    <p>
                        <div style="text-align: center; margin: 20px 0;">
                            <a href="http://localhost:5173/login" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Go to Login</a>
                        </div>
                    </p>
                    
                    <p>If you have any questions or issues logging in, please contact the administrator.</p>
                    
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e0e0e0;">
                    <p style="font-size: 12px; color: #666;">
                        <strong>Note:</strong> This is an automated email. Please do not reply to this email address.
                    </p>
                </div>
            </body>
        </html>
        """
        
        message = Mail(
            from_email=Email(SENDER_EMAIL, "Clinical Rotation System"),
            to_emails=To(student_email),
            subject=subject,
            html_content=html_content
        )
        
        print(f"[EMAIL] Sending email via SendGrid...")
        response = sg.send(message)
        print(f"[EMAIL SUCCESS] Email sent! Status Code: {response.status_code}")
        print(f"[EMAIL SUCCESS] Response headers: {response.headers}")
        return True
        
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email!")
        print(f"[EMAIL ERROR] Error type: {type(e).__name__}")
        print(f"[EMAIL ERROR] Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
