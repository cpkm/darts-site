from flask import render_template, current_app
from app.email import send_bulk_email

def send_reminder_email(users, match, status):
    print('sending email to {} for {} match.'.format(users,match))
    token = [u.get_user_token(task='checkin') for u in users]
    send_bulk_email('ICC4 Event reminder: {} vs {}'.format(match.date.strftime('%d-%b'), match.opponent.name),
              sender=current_app.config['ADMINS'][0],
              recipients=[u.email for u in users],
              text_body=[render_template('email/event_reminder.txt', 
                match=match, user=u, status=s, token=t) for u,s,t in zip(users,status,token)],
              html_body=[render_template('email/event_reminder.html', 
                match=match, user=u, status=s, token=t) for u,s,t in zip(users,status,token)])