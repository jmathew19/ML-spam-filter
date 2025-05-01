import os
import base64
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes

# Constants
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
API_URL = os.getenv("SPAM_API_URL", "http://172.190.112.177/predict")  # replace or set env var

SPAM_COLOR = {
    "backgroundColor": "#711a36",  # Gmail-safe red
    "textColor": "#000000"
}


HAM_COLOR = {
    "backgroundColor": "#16a766",  # Gmail-safe green
    "textColor": "#000000"
}

# --- Gmail Auth ---
def authenticate_gmail():
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
    # CREDENTIALS_PATH = 'Credentials/Google/credentials.json'
    # TOKEN_PATH = 'Credentials/Google/token.json'
    CREDENTIALS_PATH = '/home/azureuser/secrets/credentials.json'
    TOKEN_PATH = '/home/azureuser/secrets/token.json'


    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            # auth_url, _ = flow.authorization_url(prompt='consent')
            # print(f"\n🔐 Go to this URL and log in:\n{auth_url}\n")
            # code = input("🔑 Paste the authorization code here: ")
            # # flow.fetch_token(code=code)
            # flow.fetch_token(code=code, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            # creds = flow.credentials
            creds = flow.run_local_server(port=8080)
        with open(TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)



# --- Create Label if Needed ---
def get_or_create_label(service, label_name, color):
    labels = service.users().labels().list(userId='me').execute()['labels']
    for label in labels:
        if label['name'] == label_name:
            # Update color if already exists
            service.users().labels().update(
                userId='me',
                id=label['id'],
                body={"color": color}
            ).execute()
            return label['id']

    label = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show',
        'color': color
    }
    result = service.users().labels().create(userId='me', body=label).execute()
    return result['id']

# --- Main Process ---
def classify_and_label_emails():
    service = authenticate_gmail()
    spam_label = get_or_create_label(service, "SpamGuard-Spam", SPAM_COLOR)
    ham_label = get_or_create_label(service, "SpamGuard-Ham", HAM_COLOR)

    # Get unread inbox messages
    messages = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute().get('messages', [])
    print(f"🔍 Found {len(messages)} unread emails.")

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        raw_msg = base64.urlsafe_b64decode(msg_data['raw'].encode('ASCII'))
        email_message = message_from_bytes(raw_msg)

        # Get subject + body
        subject = email_message['Subject'] or ""
        body = ""
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == 'text/plain':
                    body += part.get_payload(decode=True).decode(errors="ignore")
        else:
            body = email_message.get_payload(decode=True).decode(errors="ignore")

        text = f"{subject}\n{body}".strip()

        try:
            response = requests.post(API_URL, json={"text": text})
            prediction = response.json().get("prediction", "ham")
            label_id = spam_label if prediction == "spam" else ham_label

            service.users().messages().modify(
                userId='me',
                id=msg['id'],
                body={'addLabelIds': [label_id]}
            ).execute()

            print(f"✅ '{subject[:50]}' → {prediction.upper()}")
        except Exception as e:
            print(f"❌ Failed to classify email: {e}")

if __name__ == "__main__":
    classify_and_label_emails()
