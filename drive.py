import io
import logging
import os
import smtplib
import pandas as pd
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow

def main():
    # Define the scope: Full access to Google Drive
    SCOPES = ['https://www.googleapis.com/auth/drive']

    # Path to the client_secret.json file
    CLIENT_SECRET_FILE = '/Users/apple/python1/credentials.json'

    # Create the flow using the client secrets file from the Google API Console
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

    # This will open a new browser window for the user to log in and authorize access
    creds = flow.run_local_server(port=0)

    # Display the tokens in the console
    print('Your access token is:', creds.token)
    print('Your refresh token is:', creds.refresh_token)

if __name__ == '__main__':
    main()


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_certificate(name, event, event_id, certificate_template_path):
    try:
        image = Image.open(certificate_template_path)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 24)  # Adjust to an appropriate font and size
        
        # Add name and event ID to the certificate
        draw.text((x_position, y_position), f"Name: {name}", fill="black", font=font)
        draw.text((x_position, y_position + 50), f"Event ID: {event_id}", fill="black", font=font)
        
        output = io.BytesIO()
        image.save(output, format='PDF')
        output.seek(0)
        return output
    except Exception as e:
        logging.error(f"Failed to generate certificate for {name}: {e}")
        return None

def send_email_with_attachment(email_address, password, recipient_email, subject, pdf_attachment):
    try:
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = recipient_email
        message["Subject"] = subject

        part = MIMEApplication(pdf_attachment.read(), Name="Certificate.pdf")
        part["Content-Disposition"] = 'attachment; filename="Certificate.pdf"'
        message.attach(part)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_address, password)
            server.send_message(message)
            logging.info(f"Email sent to {recipient_email}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def save_to_google_drive(service, file_obj, filename, mime_type='application/pdf'):
    file_metadata = {'name': filename}
    media = MediaIoBaseUpload(file_obj, mimetype=mime_type)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    logging.info(f"File '{filename}' saved to Google Drive with ID: {file.get('id')}")

if __name__ == "__main__":
    # Load CSV file
    csv_file_path = '/Users/apple/Downloads/multiple/apli - Sheet1.csv'
    df = pd.read_csv(csv_file_path)

    # Google Drive setup
    service = build('drive', 'v3', credentials=Credentials.from_authorized_user_file('credentials.json'))
    df.columns = [col.strip() for col in df.columns]
    for index, row in df.iterrows():
        name = row['Name']
        event = row['Event']
        event_id = row['id']
        recipient_email = row['email']

        # Path to the certificate template for the specific event
        certificate_template_path = f'/Users/apple/python1/certificates'

        # Generate certificate
        pdf_buffer = generate_certificate(name, event, event_id, certificate_template_path)
        if pdf_buffer:
            # Send email with certificate attachment
            send_email_with_attachment(sender_email, sender_password, recipient_email, f"Certificate for {event}", pdf_buffer)
            
            # Save certificate to Google Drive
            save_to_google_drive(service, pdf_buffer, f"{name}_{event}_Certificate.pdf")
