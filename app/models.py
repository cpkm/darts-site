from flask import current_app
from datetime import date
from app import db


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
    timestamp = db.Column(db.DateTime, index=True, default=date.today())

    def __repr__(self):
        return '<Game {}>'.format(self.id)
