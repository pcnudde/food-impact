import sys
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def process_csv(input_file):
    # Read the CSV
    df = pd.read_csv(input_file)
    
    # Do some simple processing (example: add a column with row numbers)
    df['row_number'] = range(1, len(df) + 1)
    
    # Save the processed file
    df.to_csv('output.csv', index=False)

def send_email(to_email, file_path):
    """Send the processed file via email using SMTP."""
    from_email = os.environ['MAIL_USERNAME']
    password = os.environ['MAIL_PASSWORD']

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = 'Your Processed CSV Data'
    
    msg.attach(MIMEText('Please find your processed CSV data attached.'))
    
    with open(file_path, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype='csv')
        attachment.add_header('Content-Disposition', 'attachment', filename='processed_data.csv')
        msg.attach(attachment)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email, password)
        smtp.send_message(msg)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python process_csv.py <input_file>")
        sys.exit(1)
        
    process_csv(sys.argv[1])