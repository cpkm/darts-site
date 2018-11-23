from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField
from wtforms.validators import ValidationError, DataRequired, Length, Email
from app.models import Player, Game, Match, Team, PlayerGame
from app.validators import Unique

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


#class EditMatchForm(FlaskForm):
