from app import create_app, db
from app.models import User, Match, Player, ReminderSettings, current_roster
from datetime import date, timedelta
from app.main.email import send_reminder_email, send_captain_report


def find_match_reminders():

    reminders = ReminderSettings.query.filter_by(category='match reminder').all()
    print(reminders)
    match_reminders = []
    for r in reminders:
        print(r)
        dia = date.today() + timedelta(r.days_in_advance)
        matches = Match.query.filter(Match.date >= date.today(), Match.date <= dia).all()
        print(matches)
        for m in matches:
            print(m)
            if m.reminder_email_sent: 
                if ((m.date-m.reminder_email_sent) <= timedelta(r.days_in_advance)):
                    print('email sent already')
                    pass
                else:
                    print('email sent earlier')
                    if m not in match_reminders:
                        print('added')
                        match_reminders.append(m)
            else:
                print('no email previous')
                if m not in match_reminders:
                    print('added')
                    match_reminders.append(m)

    print(match_reminders)

    return match_reminders


def find_captain_reports():

    reminders = ReminderSettings.query.filter_by(category='captain report').all()
    print(reminders)
    match_reminders = []
    for r in reminders:
        print(r)
        dia = date.today() + timedelta(r.days_in_advance)
        matches = Match.query.filter(Match.date >= date.today(), Match.date <= dia).all()
        print(matches)
        for m in matches:
            print(m)
            if m.captain_report_sent: 
                if ((m.date-m.captain_report_sent) <= timedelta(r.days_in_advance)):
                    print('email sent already')
                    pass
                else:
                    print('email sent earlier')
                    if m not in match_reminders:
                        print('added')
                        match_reminders.append(m)
            else:
                print('no email previous')
                if m not in match_reminders:
                    print('added')
                    match_reminders.append(m)

    print(match_reminders)

    return match_reminders


def process_match_reminders():
    match_reminders = find_match_reminders()
    
    for m in match_reminders:
        try:
            users = [p.user for p in current_roster('active') if p.user is not None]
            status = [u.player.checked_matches_association.filter_by(match_id=m.id).first().status for u in users]
            
            print('send_reminder_email', m)
            send_reminder_email(users=users,match=m,status=status)
            m.reminder_email_sent = date.today()
            db.session.add(m)
            db.session.commit()
        except Exception as e:
            print('Error sending reminder:', e)


def process_captain_reports():
    match_reminders = find_captain_reports()
    captain = User.query.join(Player).filter(Player.role=='captain').all()

    if not captain:
        print('Error sending captain report: no captain found')
        return False
    
    for m in match_reminders:
        try:
            print('send_captain_report', m)
            send_captain_report(captain=captain,match=m)
            m.captain_report_sent = date.today()
            db.session.add(m)
            db.session.commit()
        except Exception as e:
            print('Error sending captain report:', e)


app = create_app()

if app.config['ENV']=='production':
    if not app.config['DEBUG']:
        app.config['SERVER_NAME'] = 'icc4darts.com'
    else:
        app.config['SERVER_NAME'] = 'staging.icc4darts.com'

with app.app_context(), app.test_request_context():
    process_match_reminders()
    process_captain_reports()

