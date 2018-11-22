from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import Player, Game, Match, Team, PlayerGame
from app.validators import Unique

class EditPlayerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired(), Unique(Player.nickname)])
    submit = SubmitField('Submit')