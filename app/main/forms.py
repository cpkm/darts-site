from flask import request, flash
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, RadioField, 
    FieldList, FormField, DateField, SelectField, IntegerField, HiddenField)
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length, Email
from app import db
from app.models import Player, Game, Match, Team, PlayerGame, Season, HighScore, LowScore, season_from_date
from app.validators import Unique
from datetime import datetime

class EditPlayerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    submit_new = SubmitField('Submit')
    submit_edit = SubmitField('Edit Player')
    submit_delete = SubmitField('Delete Player')

    def __init__(self, original_nickname, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_nickname = original_nickname

    def validate_nickname(self, nickname):
        if self.original_nickname != nickname.data:
            new_player_test = Player.query.filter_by(nickname=nickname.data).first()
            if new_player_test is not None and self.original_nickname is not nickname.data:
                raise ValidationError('Player nickname must be unique.')

class ActivePlayerForm(FlaskForm):
    player = HiddenField('', validators=[DataRequired()])
    is_active = BooleanField('')

class RosterForm(FlaskForm):
    roster = FieldList(FormField(ActivePlayerForm))
    submit = SubmitField('Submit Roster')

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def fill_roster(self):
        all_players = Player.query.filter(~Player.nickname.in_(['Dummy','Sub'])).order_by(Player.nickname).all()

        for i,p in enumerate(all_players):
            self.roster.append_entry()
            self.roster[i].player.data = p
            self.roster[i].is_active.data = p.is_active

class ClaimPlayerForm(FlaskForm):
    player = SelectField('', choices=[], default='--Select Player--')
    submit_claim = SubmitField('Claim Player')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        unclaimed_players = Player.query.filter(Player.nickname!='Dummy').filter(Player.user==None).all()
        players = [(p.nickname,p.nickname+' ('+p.first_name+' '+p.last_name+')') for p in unclaimed_players]
        self.player.choices = players

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
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today().date, validators=[DataRequired()])
    opponent = SelectField('Opponent', choices=[], validators=[DataRequired()])
    home_away = RadioField('Location', choices=[('home','Home'),('away','Away')], default='home', validators=[DataRequired()])
    match_type = RadioField('Match Type', choices=[('r','Regular'),('p','Playoffs')], default='r', validators=[DataRequired()])

    submit_new = SubmitField('Submit')
    submit_edit = SubmitField('Edit Match')
    submit_delete = SubmitField('Delete Match')

    def __init__(self, match=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if match is not None:
            self.original_date = match.date
            self.original_opponent = match.opponent.name
            self.original_home_away = match.home_away
            self.original_match_type = match.match_type
        else:
            self.original_date = None
            self.original_opponent = None
            self.original_home_away = None
            self.original_match_type = None

    def load_match(self, match):
        self.date.data = match.date
        self.opponent.data = match.opponent.name
        self.home_away.data = match.home_away
        self.match_type.data = match.match_type


    def validate_opponent(self, opponent):
        opp_id = Team.query.filter_by(name=opponent.data).first().id
        if (self.original_date==self.date.data and self.original_opponent==opponent.data
         and self.original_home_away==self.home_away.data and self.original_match_type==self.match_type.data):
            flash('Match details unchanged.', 'warning')
            raise ValidationError('Match details did not change.')
        if Match.query.filter_by(date=self.date.data, home_away=self.home_away.data, 
                opponent_id=opp_id, match_type=self.match_type.data).first() is not None:
            flash('Match must be unique! Match not added', 'danger')
            raise ValidationError('Match details are not unique.')


class DoublesGameForm(FlaskForm):
    p1 = SelectField('', choices=[], default='Dummy')
    p2 = SelectField('', choices=[], default='Dummy')
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
    p1 = SelectField('', choices=[], default='Dummy')
    p1_stars = SelectField('', choices=[('0','0'),('1','1'),('2','2')], default='0')
    win = BooleanField('Win')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roster = Player.query.all()
        player_choices = [(p.nickname,p.nickname) for p in roster]
        self.p1.choices=player_choices


class EnterScoresForm(FlaskForm):
    win = BooleanField('Match won')
    overtime = BooleanField('Overtime')
    team_score = IntegerField('Us', validators=[InputRequired()])
    opponent_score = IntegerField('Them', validators=[InputRequired()])
    food = StringField('Food')
    match_summary = TextAreaField('Game summary', validators=[Length(min=0, max=320)])

    d701 = FieldList(FormField(DoublesGameForm), min_entries=4, max_entries=4)
    d501 = FieldList(FormField(DoublesGameForm), min_entries=4, max_entries=4)
    s501 = FieldList(FormField(SinglesGameForm), min_entries=8, max_entries=8)

    submit_scores = SubmitField('Submit Scores')
    submit_details = SubmitField('Submit Details')

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.d701:
            f.p1_stars.choices =[('0','0'),('1','1')]
            f.p2_stars.choices =[('0','0'),('1','1')]

    def load_games(self, match):
        if match.games.all() is None:
            return

        d701 = match.games.filter_by(game_type='doubles 701').order_by(Game.game_num).all()
        d501 = match.games.filter_by(game_type='doubles 501').order_by(Game.game_num).all()
        s501 = match.games.filter_by(game_type='singles 501').order_by(Game.game_num).all()

        if d701 is not None:
            for i,game in enumerate(d701):
                player_game = game.players_association.all()
                nop = len(player_game)
                self.d701[i].win.data = game.win
                if nop==2:
                    self.d701[i].p1.data = player_game[0].player.nickname
                    self.d701[i].p2.data = player_game[1].player.nickname
                    self.d701[i].p1_stars.data = str(player_game[0].stars)
                    self.d701[i].p2_stars.data = str(player_game[1].stars)
                elif nop==1:
                    self.d701[i].p1.data = player_game[0].player.nickname
                    self.d701[i].p1_stars.data = player_game[0].stars
                else:
                    pass

        if d501 is not None:
            for i,game in enumerate(d501):
                player_game = game.players_association.all()
                nop = len(player_game)
                self.d501[i].win.data = game.win
                if nop==2:
                    self.d501[i].p1.data = player_game[0].player.nickname
                    self.d501[i].p2.data = player_game[1].player.nickname
                    self.d501[i].p1_stars.data = str(player_game[0].stars)
                    self.d501[i].p2_stars.data = str(player_game[1].stars)
                elif nop==1:
                    self.d501[i].p1.data = player_game[0].player.nickname
                    self.d501[i].p1_stars.data = str(player_game[0].stars)
                else:
                    pass

        if s501 is not None:
            for i,game in enumerate(s501):
                player_game = game.players_association.all()
                nop = len(player_game)
                self.s501[i].win.data = game.win
                if nop==1:
                    self.s501[i].p1.data = player_game[0].player.nickname
                    self.s501[i].p1_stars.data = str(player_game[0].stars)
                else:
                    pass
        return


class HLPlayerScoreForm(FlaskForm):
    player = SelectField('', choices=[], default='Dummy')
    high_scores = FieldList(IntegerField('Score'), min_entries=12, max_entries=12)
    low_scores = FieldList(IntegerField('Score'), min_entries=12, max_entries=12)


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roster = Player.query.all()
        player_choices = [(p.nickname,p.nickname) for p in roster]
        self.player.choices = player_choices


class HLScoreForm(FlaskForm):
    hl_scores = FieldList(FormField(HLPlayerScoreForm), min_entries=4,max_entries=24)
    add_btn = SubmitField('+')
    rem_btn = SubmitField('-')

    submit_hl_scores = SubmitField('Submit scores')

    def save_scores(self, match):
        for row in self.hl_scores:
            if row.player.data != 'Dummy':
                player = Player.query.filter_by(nickname=row.player.data).first()
                for hs in row.high_scores:
                    if hs.data is not None:
                        entry = HighScore(player=player, score=hs.data, match_id=match.id)
                        db.session.add(entry)
                        db.session.commit()
                for ls in row.low_scores:
                    if ls.data is not None:
                        entry = LowScore(player=player, score=ls.data, match_id=match.id)
                        db.session.add(entry)
                        db.session.commit()
        return

    def load_scores(self, match):
        if match.high_scores.all() is None and match.low_scores.all() is None:
            return

        all_p = match.get_roster()
        diff = len(all_p) - len(self.hl_scores)

        if diff > 0:
            for _ in range(diff):
                self.hl_scores.append_entry()

        for i,p in enumerate(all_p):
            self.hl_scores[i].player.data = p.nickname
            for j,s in enumerate(match.high_scores.filter_by(player=p).all()):
                if j < self.hl_scores[i].high_scores.max_entries:
                    self.hl_scores[i].high_scores[j].data = s.score

            for j,s in enumerate(match.low_scores.filter_by(player=p).all()):
                if j < self.hl_scores[i].low_scores.max_entries - 1:
                    self.hl_scores[i].low_scores[j].data = s.score
        return

            





