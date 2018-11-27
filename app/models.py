from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import date as date
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

    def game_stars(self, game=None, game_id=None):
        if game:
            return self.games_association.filter_by(game=game).first().stars
        return self.games_association.filter_by(game_id=game_id).first().stars

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

        games = Game.query.filter_by(match=self).all()
        for g in games:
            db.session.delete(g)
        db.session.commit()


    def set_location(self):
        if self.opponent is not None:
            if self.home_away == 'away':
                self.location = self.opponent.home_location
            else:
                self.location = 'Italian Canadian Club'

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


class PlayerSeasonStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db. ForeignKey('player.id'))
    player = db.relationship('Player')
    season_id = db.Column(db.Integer, db. ForeignKey('season.id'))
    season = db.relationship('Season')
    matches_played = db.Column(db.Integer, primary_key=True)
    matches_won = db.Column(db.Integer, primary_key=True)
    matches_lost = db.Column(db.Integer, primary_key=True)
    games_played = db.Column(db.Integer, primary_key=True)
    games_won = db.Column(db.Integer, primary_key=True)
    total_stars = db.Column(db.Integer, primary_key=True)
    total_high_scores = db.Column(db.Integer, primary_key=True)
    total_low_scores = db.Column(db.Integer, primary_key=True)

class TeamSeasonStatistics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db. ForeignKey('team.id'))
    team = db.relationship('Team')
    season_id = db.Column(db.Integer, db. ForeignKey('season.id'))
    season = db.relationship('Season')
    matches_played = db.Column(db.Integer, primary_key=True)
    matches_won = db.Column(db.Integer, primary_key=True)
    matches_lost = db.Column(db.Integer, primary_key=True)
    games_played = db.Column(db.Integer, primary_key=True)
    games_won = db.Column(db.Integer, primary_key=True)
    total_stars = db.Column(db.Integer, primary_key=True)
    total_high_scores = db.Column(db.Integer, primary_key=True)
    total_low_scores = db.Column(db.Integer, primary_key=True)


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season_name = db.Column(db.String(64), index=True, unique=True)
    start_date = db.Column(db.Date, index=True)
    end_date = db.Column(db.Date, index=True)


