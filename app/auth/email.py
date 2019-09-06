from flask import render_template, current_app
from app.email import send_email

def send_password_reset_email(user):
    token = user.get_user_token(task='reset_password')
    send_email('[ICC4] Reset Your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_verification_email(user):
    token = user.get_user_token(task='verify_email', expires_in=86400)
    send_email('[ICC4] Verify Your account',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/verify_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/verify_email.html',
                                         user=user, token=token))