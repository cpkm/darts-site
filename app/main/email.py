from flask import render_template, current_app
from app.email import send_bulk_email, send_email

def send_reminder_email(users, match, status):

    allowed = [True]*len(users)
    ins,out,ifn,nrp = match.get_checked_players()
    u_nrp = [i.player.user for i in nrp]

    for i,u in enumerate(users):
        if u.settings:
            if u.settings.email_reminders:
                if u.settings.email_reminders_if_nr and u not in u_nrp:
                    allowed[i] = False
            else:
                allowed[i] = False

    print(allowed)

    users,status = [[i for (i,t) in zip(j,allowed) if t] for j in [users,status]]
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

def send_summary_email(users, match, performers):
    allowed = [u.settings.email_summary if u.settings is not None else True for u in users] 
    users = [i for (i,t) in zip(users,allowed) if t]
    print('sending summary email to {} for {} match.'.format(users,match))
    send_email('ICC4 Event summary: {} vs {}'.format(match.date.strftime('%d-%b'), match.opponent.name),
            sender=current_app.config['ADMINS'][0],
            recipients=[],
            text_body=render_template('email/event_summary.txt', match=match, performers=performers),
            html_body=render_template('email/event_summary.html', match=match, performers=performers),
            bcc=[u.email for u in users])
