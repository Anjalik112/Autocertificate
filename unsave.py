from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pandas as pd
from io import BytesIO

# Load CSV file
csv_file_path = '/Users/apple/Downloads/multiple/apli - Sheet1.csv'
df = pd.read_csv(csv_file_path)

# Clean up column names by stripping whitespace
df.columns = [col.strip() for col in df.columns]

# Email Credentials
sender_email = "info@ignitestudentassociation.com"
sender_password = "qejl hhpa vppx jwcg"  # Replace with your actual app password

# Certificate Templates based on events
certificate_templates = {
    'Quiz': '/Users/apple/python1/certificates/Quiz_certificate.png',
    'Coding': '/Users/apple/python1/certificates/coding_certificate copy.png',
    'VideoEditing': '/Users/apple/Downloads/VideoEditing_certificate.png',
    'UiUx': '/Users/apple/python1/certificates/UiUx_certificate.png',
    'Esports': '/Users/apple/python1/certificates/Esports_certificate.png',
    'Propmt': '/Users/apple/python1/certificates/promptgenration_certificate.png',
}

# Font settings
bold_font_path = '/Library/Fonts/Arial Bold.ttf'
font_size = 250
bold_font = ImageFont.truetype(bold_font_path, font_size)
font1_size = 100
font1_path = '/Library/Fonts/Arial.ttf'
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
    width, height = image.size

    # Manually adjusted positions for demonstration
    name_x_position = 500  # Adjust as needed
    name_y_position = 300  # Adjust as needed
    id_x_position = 500  # Adjust as needed
    id_y_position = 400  # Adjust as needed

    # Drawing text without calculating its size
    draw.text((name_x_position, name_y_position), name, fill="black", font=bold_font)
    draw.text((id_x_position, id_y_position), f"ID: {event_id}", fill="black", font=font1)

    # Convert the image to a byte stream instead of saving it
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format='JPEG')
    img_byte_arr = img_byte_arr.getvalue()

    return img_byte_arr


def send_email(recipient_email, certificate_bytes, event, recipient_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Your Certificate for {event}"

        body = f"Please find attached your certificate for participating in the {event}."
        msg.attach(MIMEText(body, 'plain'))

        # Attach the certificate from the byte stream
        msg.attach(MIMEImage(certificate_bytes, name=f"{event}_certificate.jpg"))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg, sender_email, recipient_email)
        server.quit()

        print(f"Mail sent to {recipient_name}")  # Print confirmation after sending
    except Exception as e:
        print(f"Error sending email to {recipient_email} for event {event}: {e}")


# Iterate over each row in the dataframe
for index, row in df.iterrows():
    name = row['Name']
    email = row['email']
    event = row['Event']
    event_id = row['id']

    certificate_bytes = generate_certificate(name, event, event_id)
    if certificate_bytes:
        send_email(email, certificate_bytes, event, name)
