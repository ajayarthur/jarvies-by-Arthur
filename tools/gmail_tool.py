import os
import base64
from email.message import EmailMessage
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from livekit.agents import function_tool

SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def get_gmail_service():
    """
    Creates Gmail API service client.
    Uses token.json for refreshable login.
    """

    creds = None

    if os.path.exists("gmail_token.json"):
        creds = Credentials.from_authorized_user_file("gmail_token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            os.getenv("GMAIL_CLIENT_SECRETS_JSON"),
            SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open("gmail_token.json", "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


@function_tool
async def gmail_send_tool(to: str, subject: str, message: str) -> str:
    """
    Sends an email using Gmail API.
    """

    try:
        service = get_gmail_service()

        email = EmailMessage()
        email["To"] = to
        email["From"] = "me"
        email["Subject"] = subject
        email.set_content(message)

        encoded_message = base64.urlsafe_b64encode(email.as_bytes()).decode()

        send = service.users().messages().send(
            userId="me",
            body={"raw": encoded_message}
        ).execute()

        return f"📧 Email sent successfully to {to}"

    except Exception as e:
        return f"❌ Gmail error: {e}"
