from flask.ext.mail import Message

from app import app, mail


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=app.config['MAIL_DEFAULT_SENDER']
    )
    print app.config['MAIL_DEFAULT_SENDER'], app.config['MAIL_PORT'], app.config['MAIL_SERVER']
    mail.send(msg)