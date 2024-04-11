from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pandas as pd
from io import BytesIO
import threading

# Define the path to your CSV file
csv_file_path = '/Users/apple/python1/new/Certificate  (Responses) - UiUx.csv'
df = pd.read_csv(csv_file_path)
df.columns = [col.strip() for col in df.columns]

# Email sender details
sender_email = "info@ignitestudentassociation.com"
sender_password = "qejl hhpa vppx jwcg"

# Certificate templates by event type
certificate_templates = {
    'UiUx': '/Users/apple/python1/certificates/UiUx_certificate.png',
}

# Font settings
bold_font_path = '/Library/Fonts/Arial Bold.ttf'
font_size = 175
font_path = '/path/to/fonts/Lato-Regular.ttf'
bold_font = ImageFont.truetype(bold_font_path, font_size)
font1_size = 90
font1_path = '/path/to/fonts/Lato-Regular.ttf'
font = ImageFont.truetype(font_path, font_size)
font1 = ImageFont.truetype(font1_path, font1_size)

def generate_certificate(name, event, event_id):
    if event not in certificate_templates:
        print(f"Error: No certificate template defined for event '{event}'.")
        return None

    certificate_template_path = certificate_templates[event]
    try:
        image = Image.open(certificate_template_path)
    except FileNotFoundError:
        print(f"Error: Certificate template file '{certificate_template_path}' not found.")
        return None

    image = image.convert('RGB')
    draw = ImageDraw.Draw(image)

    # Updated text positions for better layout
    name_x_position = 3600  
    name_y_position = 2840  
    id_x_position = 6000 
    id_y_position = 3980  

    # Text color and font settings
    draw.text((name_x_position, name_y_position), name, fill=(11, 38, 81), font=font)
    draw.text((id_x_position, id_y_position), f"ID: {event_id}", fill=(11, 38, 81), font=font1)

    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='PNG')  # Switching to PNG for better quality
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr

def send_email(recipient_email, certificate_bytes, event, recipient_name):
    def send_email_thread():
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Congratulations! Your Certificate for {event} is Here🥳"

            body = f"""Dear {name},
We are thrilled to announce that your certificate for participating in {event} Competition is now available!

We appreciate your dedication and active participation in the event. Your contribution made it a valuable learning experience for everyone involved.

In this email, you will find your certificate attached as a PNG . You can print it out or save it electronically for your records.

We hope you continue to develop your skills and wish you all the best in your future endeavors.

Our Fire awaits for your Spark!
Smokey regards, 
Ignite SA. 🔥"""
            msg.attach(MIMEText(body, 'plain'))

            # MIMEImage to attach the certificate image
            image_attachment = MIMEImage(certificate_bytes)
            image_attachment.add_header('Content-Disposition', 'attachment', filename=f"{event}_certificate.png")  # Updated filename extension
            msg.attach(image_attachment)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            print(f"Mail sent to {recipient_name}")
        except Exception as e:
            print(f"Error sending email to {recipient_email} for event {event}: {e}")

    # Start the email sending in a separate thread
    email_thread = threading.Thread(target=send_email_thread)
    email_thread.start()

# Iterate over each row in the DataFrame to process participants
for index, row in df.iterrows():
    name = row['Name'].strip()  # Trim any leading/trailing whitespace
    email = row['email'].strip()
    event = row['Event'].strip()
    event_id = row['id'].strip()
    
    if pd.isna(event) or event not in certificate_templates:
        print(f"Skipping {name}, as the event is not defined or not recognized.")
        continue
    
    certificate_bytes = generate_certificate(name, event, event_id)
    if certificate_bytes:
        send_email(email, certificate_bytes, event, name)
