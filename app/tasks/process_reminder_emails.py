from app import create_app, db
from app.models import Match, Player, ReminderSettings, current_roster
from datetime import date, timedelta
from app.main.email import send_reminder_email


def find_reminder_matches(category):

    reminders = ReminderSettings.query.filter_by(category=category).all()

    for r in reminders:
        dia = date.today() + timedelta(r.days_in_advance)
        matches = Match.query.filter(Match.date >= date.today(), Match.date <= dia).all()

        for m in matches:
            if m.reminder_email_sent:
                if (m.date-m.reminder_email_sent) <= r.days_in_advance:
                    matches.remove(m)

    return matches



app = create_app()
with app.app_context():

    matches = find_reminder_matches('match reminder')

    for m in matches:
        users = [p.user for p in current_roster() if p.user is not None]
        status = [u.player.checked_matches_association.filter_by(match_id=match.id).first().status for u in users]
        
        send_reminder_email(users=users,match=m,status=status)
        match.reminder_email_sent = date.today()
        db.session.add(match)
        db.session.commit()
        #send reminder email

    print('Done!')


