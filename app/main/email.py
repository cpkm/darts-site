from flask import render_template, current_app
from app.email import send_bulk_email, send_email

def send_reminder_email(users, match, status):
    print('sending reminder email to {} for {} match.'.format(users,match))
    send_bulk_email('ICC4 Event reminder: {} vs {}'.format(match.date.strftime('%d-%b'), match.opponent.name),
            sender=current_app.config['ADMINS'][0],
            recipients=[u.email for u in users],
            text_body=[render_template('email/event_reminder.txt', 
                match=match, user=u, status=s) for u,s in zip(users,status)],
            html_body=[render_template('email/event_reminder.html', 
                match=match, user=u, status=s) for u,s in zip(users,status)])

def send_captain_report(captain, match):
    print('sending captain report email to {} for {} match.'.format(captain,match))
    send_bulk_email("ICC4 Captain's Report: {} vs {}".format(match.date.strftime('%d-%b'), match.opponent.name),
            sender=current_app.config['ADMINS'][0],
            recipients=[c.email for c in captain],
            text_body=[render_template('email/captain_report.txt', captain=c, match=match) for c in captain],
            html_body=[render_template('email/captain_report.html', captain=c, match=match) for c in captain])