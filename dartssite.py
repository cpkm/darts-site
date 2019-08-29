from app import create_app, db
from app.models import Player, Game, Match, PlayerGame, Team, Season, PlayerSeasonStats, MatchStats, User, PlayerMatchCheckin

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Player': Player, 'Game': Game, 'Match': Match, 
        'PlayerGame': PlayerGame, 'Team': Team, 'Season': Season, 
        'PlayerSeasonStats': PlayerSeasonStats, 'User': User , 'PlayerMatchCheckin':PlayerMatchCheckin}
