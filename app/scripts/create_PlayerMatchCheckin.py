from app import create_app, db
from app.models import Match, Player, PlayerMatchCheckin

print('Initializing...')
app = create_app()
with app.app_context():
    print('Preparing additions...')
    matches = Match.query.all()
    players = Player.query.all()
    pmc = [PlayerMatchCheckin(match_id=m.id,player_id=p.id) for m in matches for p in players]

    print('Committing to database...')
    db.session.add_all(pmc)
    db.session.commit()

    print('Done!')
