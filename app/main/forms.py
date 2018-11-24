from flask import request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, RadioField, FieldList, FormField, DateField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import Player, Game, Match, Team, PlayerGame
from app.validators import Unique
from datetime import datetime

class EditPlayerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    nickname = StringField('Nickname')
    submit_new = SubmitField('Submit')
    submit_edit = SubmitField('Edit Player')
    submit_delete = SubmitField('Delete Player')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_nickname = self.nickname

    def validate_nickname(self, nickname):
        if nickname.data is '':
           nickname.data = '{} {}'.format(self.first_name.data, self.last_name.data)
        new_player_test = Player.query.filter_by(nickname=nickname.data).first()
        print(self.original_nickname,nickname.data,self.original_nickname.data is not nickname.data)
        if new_player_test is not None and self.original_nickname.data is not nickname.data:
            raise ValidationError('Player nickname must be unique.')


class EditTeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired()])
    home_location = StringField('Home Bar', validators=[DataRequired()])
    address = TextAreaField('Bar Address', validators=[Length(min=1, max=140)])

    submit_new = SubmitField('Submit')
    submit_edit = SubmitField('Edit Team')
    submit_delete = SubmitField('Delete Team')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = self.name

    def validate_name(self, name):
        teamname = Team.query.filter_by(name=name.data).first()
        if teamname is not None and self.original_name.data is not name.data:
            raise ValidationError('Team name must be unique.')


class EditMatchForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    opponent = StringField('Opponent', validators=[DataRequired()])
    home_away = RadioField('Location', choices=[('home','Home'),('away','Away')], validators=[DataRequired()])

    submit_new = SubmitField('Submit')
    submit_edit = SubmitField('Edit Match')
    submit_delete = SubmitField('Delete Match')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_date = self.date
        self.original_opponent = self.opponent
        self.original_home_away = self.home_away

    def validate_opponent(self, opponent):
        opp_id = Team.query.filter_by(name=opponent.data).first().id

        #if self.date==self.original_date and self.original_opponent==opponent and self.original_home_away==self.home_away:
        #    flash('Match details unchanged.', 'warning')
        #    raise ValidationError('Match details did not change.')

        if Match.query.filter_by(date=self.date.data, home_away=self.home_away.data, opponent_id=opp_id).first() is not None:
            flash('Match must be unique! Match not added', 'danger')
            raise ValidationError('Match details are not unique.')

class DoublesGameForm(FlaskForm):
    p1 = StringField('Player 1', validators=[DataRequired()])
    p2 = StringField('Player 2', validators=[DataRequired()])

    submit = SubmitField('Submit')
