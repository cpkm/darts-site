from flask import current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
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

player_game = db.Table('player_game',
        db.Column('player_id', db.Integer, db.ForeignKey('player.id')),
        db.Column('game_id', db.Integer, db.ForeignKey('game.id')))


class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    about_me = db.Column(db.String(140))

    games = db.relationship('Game', 
        secondary=player_game, 
        backref=db.backref('players', lazy='dynamic'), lazy='dynamic')


    def __repr__(self):
        return '<Player {}>'.format(self.name)


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'))
    game_num = db.Column(db.Integer, index=True)
    game_type = db.Column(db.String(64), index=True)

    def __repr__(self):
        return '<Game {}>'.format(self.id)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=date.today())
    opponent = db.Column(db.String(64), index=True)
    home_game = db.Column(db.Boolean, index=True, default=True)
    games = db.relationship('Game', backref='match', lazy='dynamic')

    def __repr__(self):
        return '<Match {}>'.format(self.date)