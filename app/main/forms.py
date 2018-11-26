from flask import request, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, RadioField, FieldList, FormField, DateField, SelectField
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
    opponent = SelectField('Opponent', choices=[], validators=[DataRequired()])
    home_away = RadioField('Location', choices=[('home','Home'),('away','Away')], default='home', validators=[DataRequired()])

    submit_new = SubmitField('Submit')
    submit_edit = SubmitField('Edit Match')
    submit_delete = SubmitField('Delete Match')

    def __init__(self, match=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(match, match is not None)
        if match is not None:
            self.original_date = match.date
            self.original_opponent = match.opponent.name
            self.original_home_away = match.home_away
        else:
            self.original_date = None
            self.original_opponent = None
            self.original_home_away = None

    def load_match(self, match):
        self.date.data = match.date
        self.opponent.data = match.opponent.name
        self.home_away.data = match.home_away


    def validate_opponent(self, opponent):
        opp_id = Team.query.filter_by(name=opponent.data).first().id

        print(self.date.data,self.home_away.data,opponent.data)
        print(self.original_date,self.original_home_away,self.original_opponent)

        if self.original_date==self.date.data and self.original_opponent==opponent.data and self.original_home_away==self.home_away.data:
            flash('Match details unchanged.', 'warning')
            raise ValidationError('Match details did not change.')

        if Match.query.filter_by(date=self.date.data, home_away=self.home_away.data, opponent_id=opp_id).first() is not None:
            flash('Match must be unique! Match not added', 'danger')
            raise ValidationError('Match details are not unique.')


class DoublesGameForm(FlaskForm):
    p1 = SelectField('', choices=[], default='Dummy', validators=[DataRequired()])
    p2 = SelectField('', choices=[], default='Dummy', validators=[DataRequired()])
    p1_stars = SelectField('', choices=[('0','0'),('1','1'),('2','2')], default='0')
    p2_stars = SelectField('', choices=[('0','0'),('1','1'),('2','2')], default='0')
    win = BooleanField('Win')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roster = Player.query.all()
        player_choices = [(p.nickname,p.nickname) for p in roster]
        self.p1.choices=player_choices
        self.p2.choices=player_choices


class SinglesGameForm(FlaskForm):
    p1 = SelectField('', choices=[], default='Dummy', validators=[DataRequired()])
    p1_stars = SelectField('', choices=[('0','0'),('1','1'),('2','2')], default='0')
    win = BooleanField('Win')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roster = Player.query.all()
        player_choices = [(p.nickname,p.nickname) for p in roster]
        self.p1.choices=player_choices


class EnterScoresForm(FlaskForm):
    d701 = FieldList(FormField(DoublesGameForm), min_entries=4)
    d501 = FieldList(FormField(DoublesGameForm), min_entries=4)
    s501 = FieldList(FormField(SinglesGameForm), min_entries=8)

    submit = SubmitField('Submit Scores')


