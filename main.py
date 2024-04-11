from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pandas as pd
import os

# Load CSV file
csv_file_path = '/Users/apple/Downloads/multiple/apli - Sheet1.csv'
df = pd.read_csv(csv_file_path)

# Clean up column names by stripping whitespace
df.columns = [col.strip() for col in df.columns]

# Email Credentials
sender_email = "info@ignitestudentassociation.com"
sender_password = "qejl hhpa vppx jwcg"  # Replace with your actual App Password

# Certificate Templates based on events
certificate_templates = {
    'Quiz': '/Users/apple/python1/certificates/Quiz_certificate.png',
    'Coding': '/Users/apple/python1/certificates/coding_certificate copy.png',
    'VideoEditing': '/Users/apple/Downloads/VideoEditing_certificate.png',
    'UiUx': '/Users/apple/python1/certificates/UiUx_certificate.png',
    'Esports': '/Users/apple/python1/certificates/Esports_certificate.png',
    'Propmt': '/Users/apple/python1/certificates/promptgenration_certificate.png',
    # Add other events and their certificate paths here
}

# Bold Font
font_path = '/Library/Fonts/Arial.ttf'
font1_path='/Library/Fonts/Arial.ttf'
bold_font_path = '/Library/Fonts/Arial Bold.ttf'  # Update with the correct path to your Arial Bold font file
font_size = 250
bold_font = ImageFont.truetype(bold_font_path, font_size)
font1_size = 100
font = ImageFont.truetype(font_path, font_size)
font1 = ImageFont.truetype(font1_path, font1_size)

def generate_certificate(name, event, event_id):
    # Select the appropriate certificate template based on the event
    certificate_template_path = certificate_templates.get(event, '/Users/apple/python1/certificates')
    try:
        image = Image.open(certificate_template_path)
    except FileNotFoundError:
        print(f"Error: Certificate template file '{certificate_template_path}' not found.")
        return None

    image = image.convert('RGB')  # Convert the image to RGB mode
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # Adjust the scaling factor for the name
    text_width = len(name) * font_size * 0.7
    # Calculate x position to center the name, adjust to shift right as needed
    x_position = (width - text_width) / 2 + 1600  

    # Draw the name in bold
    draw.text((x_position, height / 2 - 105), name, fill="black", font=bold_font)
    
    # Draw the event_id (not bold)
    event_id_text = f"ID: {event_id}"
    text_width = len(event_id_text) * font1_size * 0.8  # Adjust the scaling factor as needed
    y_position = height / 2 + 1000 
    x_position = (width - text_width )/ 2 + 60
    # Adjust this value as needed to position the text vertically
    draw.text((width - text_width, y_position, x_position), event_id_text, fill="black", font=font1)  # Use bold_font if you want the ID bold as well

    # Save certificate
    os.makedirs('certificates', exist_ok=True)  # Ensure the certificates directory exists
    certificate_path = f'certificates/{name}_{event}.jpg'
    image.save(certificate_path)
    return certificate_path

def send_email(recipient_email, certificate_path, event):
    try:
        # Setup email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Your Certificate for {event}"
        body = f"Please find attached your certificate for participating in the {event}."
        msg.attach(MIMEText(body, 'plain'))

        # Attach certificate
        with open(certificate_path, 'rb') as file:
            msg.attach(MIMEImage(file.read(), name=os.path.basename(certificate_path)))

        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail's SMTP server
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg, sender_email, recipient_email)
        server.quit()
    except Exception as e:
        print(f"Error sending email to {recipient_email} for event {event}: {e}")

# Iterate over each row in the dataframe
for index, row in df.iterrows():
    name = row['Name']
    email = row['email']
    event = row['Event']  # Adjusted to account for stripped whitespace in column names
    event_id = row['id']

    # Generate and send certificates based on the event
    certificate_path = generate_certificate(name, event, event_id)
    if certificate_path:
        send_email(email, certificate_path, event)
        print(f"Sent {event} certificate to {name}")
