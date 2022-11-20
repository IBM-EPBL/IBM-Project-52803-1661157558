import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail
from_email='aaabimanyou@gmail.com',
to_emails= 'user'
subject='Sending with Twilio SendGrid is Fun',
html_content='<strong>and easy to do anywhere, even with Python</strong>'
try:
    sg = SendGridAPIClient(os.environ.get('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'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)
