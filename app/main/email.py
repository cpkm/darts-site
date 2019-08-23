from flask import render_template, current_app
from app.email import send_bulk_email

def send_reminder_email(users, match):
    print('sending email to {} for {} match.'.format(users,match))
    token = [u.get_user_token(task='checkin') for u in users]
    send_bulk_email('ICC4 Event reminder: {} at {}'.format(match.date.strftime('%d-%b'), match.location),
              sender=current_app.config['ADMINS'][0],
              recipients=[u.email for u in users],
              text_body=[render_template('email/event_reminder.txt', match=match, user=u, token=t) for u,t in zip(users,token)],
              html_body=[render_template('email/event_reminder.html', match=match, user=u, token=t) for u,t in zip(users,token)])