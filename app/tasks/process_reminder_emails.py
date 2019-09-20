from app import create_app, db
from app.models import Match, Player, ReminderSettings, current_roster
from datetime import date, timedelta
from app.main.email import send_reminder_email


def find_match_reminders(category):

    reminders = ReminderSettings.query.filter_by(category=category).all()
    print(reminders)
    match_reminders = []
    for r in reminders:
        dia = date.today() + timedelta(r.days_in_advance)
        matches = Match.query.filter(Match.date >= date.today(), Match.date <= dia).all()

        for m in matches:
            if m.reminder_email_sent:
                if (m.date-m.reminder_email_sent) <= timedelta(r.days_in_advance):
                    matches.remove(m)

        match_reminders.append(matches)

    return match_reminders



app = create_app()
with app.app_context(), app.test_request_context():

    match_reminders = find_match_reminders('match reminder')
    
    for matches in match_reminders:
        for m in matches:
            try:
                users = [p.user for p in current_roster() if p.user is not None]
                status = [u.player.checked_matches_association.filter_by(match_id=m.id).first().status for u in users]
                
                send_reminder_email(users=users,match=m,status=status)
                m.reminder_email_sent = date.today()
                db.session.add(m)
                db.session.commit()
            except Exception as e:
                print('Error sending reminder:', e)