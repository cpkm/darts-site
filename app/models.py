from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from datetime import date as date
from app import db


# naming_convention = {
#     "ix": 'ix_%(column_0_label)s',
#     "uq": "uq_%(table_name)s_%(column_0_name)s",
#     "ck": "ck_%(table_name)s_%(column_0_name)s",
#     "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
#     "pk": "pk_%(table_name)s",
# }
# db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

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
    name = db.Column(db.String(64), index=True, unique=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    about_me = db.Column(db.String(140))
    games = association_proxy('games_association', 'game')

    def game_stars(self, game=None, game_id=None):
        if game:
            return self.games_association.filter_by(game=game).first().stars
        return self.games_association.filter_by(game_id=game_id).first().stars

    def __repr__(self):
        return '<Player {}>'.format(self.name)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    game_num = db.Column(db.Integer, index=True)
    game_type = db.Column(db.String(64), index=True)
    win = db.Column(db.Boolean, index=True, default=True)
    players = association_proxy('players_association', 'player')

    def __repr__(self):
        return '<Game {:02d}, {}>'.format(self.game_num, self.match.date) if self.match \
            else '<Game_id {}>'.format(self.id)


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, index=True, default=date.today())
    opponent = db.Column(db.String(64), index=True)
    home_game = db.Column(db.Boolean, index=True, default=True)
    games = db.relationship('Game', backref='match', lazy='dynamic')

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

    def __repr__(self):
        return '<Match {}>'.format(self.date)