import smtplib
import os
import imghdr
from email.message import EmailMessage
import click
import json

EMAIL_PASSWORD = os.getenv('LINKNOTIFICATIONS_GMAIL_PASSWORD')
EMAIL_ADDRESS = os.getenv('LINKNOTIFICATIONS_GMAIL')

# @click.command(help='Sends email to the desired contacts')
# @click.option('--to-contacts', required=True, help='A list of users you want to send to')
# @click.option('--msg-content', required=True, help='What is the desired content')
# @click.option('--subject', default='Github Oracle Report', help='Subject')
# @click.pass_context
def send_email(to_contacts, msg_content, subject):
# contacts = ['linknotificationspatrick@gmail.com', 'doodlmyr@gmail.com']
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_contacts.split(",")

    #msg.set_content('This is a plain text email')
    # this will take precendt if chosen
    number_of_projects = ''
    code = ''
    for oracle_project in json.loads(msg_content):
        number_of_projects = number_of_projects + '<p>' + oracle_project + \
            ' projects: {}<p>'.format(
                len(json.loads(msg_content)[oracle_project]))
        code = code + '<p>' + oracle_project + ':{}'.format(json.loads(msg_content)[oracle_project]) + '<p>'


    print('SENDING MAIL')
    html = """\
    <!DOCTYPE html>
    <html>
        <body>
            <h1>This is week in Github Oracles!</h1>
            <h2>Number of repos that people have been active per oracle system:<h2>
            {number_of_projects}
            <h2>Repositories associated with active code<h2>
            <p>{code}<p>
        </body>
    </html>
    """.format(number_of_projects = number_of_projects, code=json.loads(msg_content))
    msg.add_alternative(html, subtype='html')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)


# if __name__ == '__main__':
#     send_email()
