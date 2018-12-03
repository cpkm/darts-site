from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, alias, func, join
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method, Comparator
from sqlalchemy.sql import select
from datetime import date, timedelta
from hashlib import md5
from app import db


class PlayerGame(db.Model):
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), primary_key=True)
    stars = db.Column(db.Integer, index=True)

    player = db.relationship('Player', backref=db.backref('games_association', lazy='dynamic'))
    game = db.relationship('Game', backref=db.backref('players_association', lazy='dynamic'))

    def __repr__(self):
        return '<Player {}, Game {}>'.format(self.player_id,self.game_id)


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    games = association_proxy('games_association', 'game')
    last_match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    last_match = db.relationship('Match', foreign_keys=[last_match_id])
    first_match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    first_match = db.relationship('Match', foreign_keys=[first_match_id])

    high_scores = db.relationship('HighScore', back_populates='player', lazy='dynamic')
    low_scores = db.relationship('LowScore', back_populates='player', lazy='dynamic')

    def avatar(self, size):
        digest = md5(self.nickname.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def game_stars(self, game=None, game_id=None):
        if game:
            return self.games_association.filter_by(game=game).first().stars
        return self.games_association.filter_by(game_id=game_id).first().stars

    def update_activity(self):
        self.last_match = Match.query.join(Game).join(PlayerGame).filter_by(player_id=self.id).order_by(Match.date.desc()).first()
        self.first_match = Match.query.join(Game).join(PlayerGame).filter_by(player_id=self.id).order_by(Match.date).first()
        db.session.commit()
        return

    def update_player_stats(self, season_label='current'):
        if season_label=='current':
            season = season_from_date(date.today())
        elif season_label=='last':
            season = season_from_date(date.today()-timedelta(365))
        else:
            season = Season.query.filter_by(season_name=season_label).first()

        if season is None:
            raise NameError('No season found')

        stats = PlayerSeasonStats.query.filter_by(player_id=self.id, season=season).first()

        if stats is None:
            stats = PlayerSeasonStats(season=season, player=self)

        player_games = PlayerGame.query.filter_by(player=self).join(Game).join(Match).\
                            filter(Match.date>=season.start_date,Match.date<=season.end_date)

        stats.matches_played = Match.query.filter(Match.date>=season.start_date,Match.date<=season.end_date).\
                                    join(Game).join(PlayerGame).filter_by(player_id=self.id).distinct().count()
        stats.matches_won = Match.query.filter_by(win=True).filter(Match.date>=season.start_date,Match.date<=season.end_date).\
                            join(Game).join(PlayerGame).filter_by(player_id=self.id).distinct().count()
        stats.matches_lost = Match.query.filter_by(win=False).filter(Match.date>=season.start_date,Match.date<=season.end_date).\
                            join(Game).join(PlayerGame).filter_by(player_id=self.id).distinct().count()

        stats.games_played = player_games.count()
        stats.games_won = Game.query.filter_by(win=True).join(PlayerGame).filter_by(player_id=self.id).\
                            join(Match).filter(Match.date>=season.start_date,Match.date<=season.end_date).count()
        stats.games_lost = Game.query.filter_by(win=False).join(PlayerGame).filter_by(player_id=self.id).\
                            join(Match).filter(Match.date>=season.start_date,Match.date<=season.end_date).count()

        stats.total_stars = sum([pg.stars for pg in player_games.all()])

        stats.total_high_scores = None
        stats.total_low_scores = None

        db.session.add(stats)
        db.session.commit()
        return

    def __repr__(self):
        return '<Player {}>'.format(self.nickname) if self.nickname else '<Player_id {}>'.format(self.id)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    match = db.relationship('Match', back_populates='games')
    game_num = db.Column(db.Integer, index=True)
    game_type = db.Column(db.String(64), index=True)
    win = db.Column(db.Boolean, index=True, default=True)
    players = association_proxy('players_association', 'player')

    def __repr__(self):
        return '<Game {:02d}, {}>'.format(self.game_num, self.match.date) if self.match \
            else '<Game_id {}>'.format(self.id)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    opponent_id = db.Column(db.Integer, db. ForeignKey('team.id'))
    opponent = db.relationship('Team', back_populates='matches')
    date = db.Column(db.Date, index=True, default=date.today())
    location = db.Column(db.String(64))
    home_away = db.Column(db.String(32), index=True)
    match_type = db.Column(db.String(32), index=True)
    games = db.relationship('Game', back_populates='match', lazy='dynamic')
    team_score = db.Column(db.Integer, index=True)
    opponent_score = db.Column(db.Integer, index=True)
    win = db.Column(db.Boolean, index=True, default=True)
    match_summary = db.Column(db.String(512))
    food = db.Column(db.String(128))

    high_scores = db.relationship('HighScore', back_populates='match', lazy='dynamic')
    low_scores = db.relationship('LowScore', back_populates='match', lazy='dynamic')

    @hybrid_property
    def season(self):
        return season_from_date(self.date)

    def add_game(self, game):
        if not self.is_game(game):
            game.match=self
            db.session.add(game)
            db.session.commit()

    def remove_game(self, game):
        if self.is_game(game):
            game.match=None
            db.session.add(game)
            db.session.commit()

    def is_game(self, game=None, game_id=None):
        if game:
            return self.games.filter_by(id=game.id).count() > 0
        return self.games.filter_by(id=game_id).count() > 0

    def delete_all_games(self):
        player_game = PlayerGame.query.join(Game).filter_by(match=self).all()
        for pg in player_game:
            db.session.delete(pg)
        db.session.commit()

        games = self.games.all()
        for g in games:
            db.session.delete(g)
        db.session.commit()

    def delete_all_books(self):
        high_scores = self.high_scores.all()
        for hs in high_scores:
            db.session.delete(hs)
        db.session.commit()
        low_scores = self.low_scores.all()
        for ls in low_scores:
            db.session.delete(ls)
        db.session.commit()

    def set_location(self):
        if self.opponent is not None:
            if self.home_away == 'away':
                self.location = self.opponent.home_location
            else:
                self.location = 'Italian Canadian Club'

    def get_roster(self):
        return Player.query.join(PlayerGame).join(Game).filter_by(match=self).all()

    def __repr__(self):
        return '<Match {}>'.format(self.date)


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    home_location = db.Column(db.String(64), index=True)
    address = db.Column(db.String(128), index=True)
    matches = db.relationship('Match', back_populates='opponent', lazy='dynamic')

    def avatar(self, size):
        digest = md5(self.name.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def __repr__(self):
        return '<Team {}>'.format(self.name)


class PlayerSeasonStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db. ForeignKey('player.id'))
    player = db.relationship('Player')
    season_id = db.Column(db.Integer, db. ForeignKey('season.id'))
    season = db.relationship('Season')
    matches_played = db.Column(db.Integer)
    matches_won = db.Column(db.Integer)
    matches_lost = db.Column(db.Integer)
    games_played = db.Column(db.Integer)
    games_won = db.Column(db.Integer)
    games_lost = db.Column(db.Integer)
    total_stars = db.Column(db.Integer)
    total_high_scores = db.Column(db.Integer)
    total_low_scores = db.Column(db.Integer)

    '''
    filters = [filter1,filter2,...]
    query....filter(*filters).count()
    '''

    @hybrid_property
    def gp(self):
        return PlayerGame.query.filter_by(player_id=self.player_id).join(Game).join(Match).\
                filter_by(season=self.season).distinct().count()
    
    @gp.expression
    def gp(cls):
        j = join(PlayerGame,Game).join(Match)
        return select([func.count(PlayerGame.player_id)]).where(PlayerGame.player_id==cls.player_id).\
        select_from(j).where(Match.season.id==cls.season_id).label('gp')

    @hybrid_property
    def gw(self):
        return PlayerGame.query.filter_by(player_id=self.player_id).join(Game).filter_by(win=True).join(Match).\
                filter_by(season=self.season).distinct().count()
    
    @gw.expression
    def gw(cls):
        j = join(PlayerGame,Game).join(Match)
        return select([func.count(PlayerGame.player_id)]).where(PlayerGame.player_id==cls.player_id).\
        select_from(j).where(Game.win==True & Match.season.id==cls.season_id).label('gw')

    @hybrid_property
    def gl(self):
        return PlayerGame.query.filter_by(player_id=self.player_id).join(Game).filter_by(win=False).join(Match).\
                filter_by(season=self.season).distinct().count()
    
    @gl.expression
    def gl(cls):
        j = join(PlayerGame,Game).join(Match)
        return select([func.count(PlayerGame.player_id)]).where(PlayerGame.player_id==cls.player_id).\
        select_from(j).where(Game.win==False & Match.season.id==cls.season_id).label('gw')



    def __repr__(self):
        return '<{} {}>'.format(self.player.nickname,self.season.season_name)

'''
class QueryComparator(Comparator):
    def operate(self, op, other):
        print(self.__clause_element__())
        print(other)
        return op(self.__clause_element__(), other)

                pg = alias(PlayerGame)
        sq=db.session.query(pg).filter_by(player_id=self.player_id).join(Game).join(Match).\
                filter_by(season=self.season).distinct().count()
'''



class TeamSeasonStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey('season.id'))
    season = db.relationship('Season')
    matches_played = db.Column(db.Integer)
    matches_won = db.Column(db.Integer)
    matches_lost = db.Column(db.Integer)
    games_played = db.Column(db.Integer)
    games_won = db.Column(db.Integer)
    total_stars = db.Column(db.Integer)
    total_high_scores = db.Column(db.Integer)
    total_low_scores = db.Column(db.Integer)

    def update_team_stats(self):
        return 


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_name = db.Column(db.String(64), index=True, unique=True)
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date, index=True)

    def __repr__(self):
        return '<Season {}>'.format(self.season_name)


class HighScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    player = db.relationship('Player', back_populates='high_scores')
    match = db.relationship('Match', back_populates='high_scores')


class LowScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    player = db.relationship('Player', back_populates='low_scores')
    match = db.relationship('Match', back_populates='low_scores')


def season_from_date(date):
    season = Season.query.filter(Season.start_date <= date).filter(Season.end_date >= date).first()
    return season

def update_all_player_stats():
    players = Player.query.all()
    for p in players:
        p.update_player_stats()
