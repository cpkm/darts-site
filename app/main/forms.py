from flask import request, flash
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField, RadioField, 
    FieldList, FormField, DateField, SelectField, IntegerField, HiddenField, FileField)
from flask_pagedown.fields import PageDownField
from wtforms.validators import ValidationError, DataRequired, InputRequired, Length, Email
from app import db
from app.models import (Player, Game, Match, Team, PlayerGame, Season, HighScore, LowScore, 
    ReminderSettings, season_from_date, current_roster)
from app.validators import Unique
from datetime import datetime, timedelta
import string

def hl_score(allowed='0123456789*oO'):
    message = 'Please enter a valid number.'

    def _hl_score(self, score):
        if not all([c in allowed for c in score.data]):
            raise ValidationError(message)
    return _hl_score

def strip_score(score,allowed='0123456789*oO'):
    not_allowed = string.printable.translate({ord(c): None for c in allowed})
    return score.translate({ord(c): None for c in not_allowed})


class EditPlayerForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    nickname = StringField('Nickname', validators=[DataRequired()])
    tagline = StringField('Tagline', validators=[Length(max=64)])
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
    role = SelectField('', 
        choices=[('player','player'),('assistant','assistant'),('captain','captain'),('sub','sub'),('retired','retired')], default='player')

class RosterForm(FlaskForm):
    roster = FieldList(FormField(ActivePlayerForm))
    submit = SubmitField('Submit Roster')

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)

    def fill_roster(self, players):
        for i,p in enumerate(players):
            self.roster.append_entry()
            self.roster[i].player.data = p.nickname
            self.roster[i].role.data = p.role

class ClaimPlayerForm(FlaskForm):
    player = SelectField('', choices=[], default='--Select Player--')
    submit_claim = SubmitField('Claim Player')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        unclaimed_players = Player.query.filter(~Player.nickname.in_(['Dummy','Sub'])).filter(Player.user==None).all()
        players = [(self.player.default,self.player.default)] + [(p.nickname,p.nickname+' ('+p.first_name+' '+p.last_name+')') for p in unclaimed_players]
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


class ImportMatchForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', default=datetime.today().date, validators=[DataRequired()])
    opponent = HiddenField('Opponent', validators=[DataRequired()])
    home_away = RadioField('Location', choices=[('home','Home'),('away','Away')], default='home', validators=[DataRequired()])
    match_type = RadioField('Match Type', choices=[('r','Regular'),('p','Playoffs')], default='r', validators=[DataRequired()])
    import_check = BooleanField('', default=True)


class ScheduleForm(FlaskForm):
    schedule = FieldList(FormField(ImportMatchForm))
    submit = SubmitField('Submit')

    def load_schedule(self, schedule):
        '''Requires Schedule object'''
        for i,match in enumerate(schedule.game_list_):
            self.schedule.append_entry()
            self.schedule[i].opponent.data = match.opponent
            self.schedule[i].date.data = match.date.date()
            self.schedule[i].match_type.data = 'r'
            if match.home:
                self.schedule[i].home_away.data = 'home'
            else:
                self.schedule[i].home_away.data = 'away'


class EditSeasonForm(FlaskForm):
    season_name = StringField('Season Name', validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', default=datetime.today().date, validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', default=(datetime.today()+timedelta(364)).date, validators=[DataRequired()])
    calendar_link = StringField('Calendar Link')

    submit_new = SubmitField('Submit')
    submit_edit = SubmitField('Edit Season')
    submit_delete = SubmitField('Delete Season')

    def __init__(self, season=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if season is not None:
            self.original_season_name = season.season_name
            self.original_start_date = season.start_date
            self.original_end_date = season.end_date
            self.original_calendar_link = season.calendar_link
        else:
            self.original_season_name = None
            self.original_start_date = None
            self.original_end_date = None
            self.original_calendar_link = None

    def load_season(self, season):
        self.season_name.data = season.season_name
        self.start_date.data = season.start_date
        self.end_date.data = season.end_date
        self.calendar_link.data = season.calendar_link


class DoublesGameForm(FlaskForm):
    p1 = SelectField('', choices=[], default='Dummy')
    p2 = SelectField('', choices=[], default='Dummy')
    p1_stars = SelectField('', choices=[('0','0'),('1','1'),('2','2')], default='0')
    p2_stars = SelectField('', choices=[('0','0'),('1','1'),('2','2')], default='0')
    win = BooleanField('Win')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roster = current_roster('ordered')
        player_choices = [(p.nickname,p.nickname) for p in roster]
        self.p1.choices=player_choices
        self.p2.choices=player_choices


class SinglesGameForm(FlaskForm):
    p1 = SelectField('', choices=[], default='Dummy')
    p1_stars = SelectField('', choices=[('0','0'),('1','1'),('2','2')], default='0')
    win = BooleanField('Win')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roster = current_roster('ordered')
        player_choices = [(p.nickname,p.nickname) for p in roster]
        self.p1.choices=player_choices


class EnterScoresForm(FlaskForm):
    win = BooleanField('Match won')
    overtime = BooleanField('Overtime')
    team_score = IntegerField('Us', validators=[InputRequired()])
    opponent_score = IntegerField('Them', validators=[InputRequired()])
    food = StringField('Food')
    match_summary = TextAreaField('Game summary', validators=[Length(min=0, max=320)])
    scoresheet = FileField('Scoresheet')
    remove_scoresheet = BooleanField('Remove?')

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
    high_scores = FieldList(StringField('Score'), min_entries=12, max_entries=12)
    low_scores = FieldList(StringField('Score'), min_entries=12, max_entries=12)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        roster = current_roster('ordered')
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
                    markers = '*o'
                    if all([hs.data is not bad for bad in ['',None]]):
                        score = strip_score(hs.data.lower(), allowed=string.digits+markers)
                        if any([m in score for m in markers]):
                            out = True
                            score = int(score.translate({ord(c): None for c in markers}))
                        else:
                            out = False
                            score = int(score)

                        entry = HighScore(player=player, score=score, out=out, match_id=match.id)
                        db.session.add(entry)
                        db.session.commit()

                for ls in row.low_scores:
                    score = strip_score(ls.data.lower(), allowed=string.digits)
                    if all([score is not bad for bad in ['',None]]):
                        score = int(score)
                        entry = LowScore(player=player, score=score, match_id=match.id)
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
                    if s.out:
                        score = str(s.score) + '*'
                    else:
                        score = str(s.score)
                    self.hl_scores[i].high_scores[j].data = score

            for j,s in enumerate(match.low_scores.filter_by(player=p).all()):
                if j < self.hl_scores[i].low_scores.max_entries - 1:
                    self.hl_scores[i].low_scores[j].data = str(s.score)
        return

class ReminderForm(FlaskForm):
    category = SelectField('Category', 
        choices=[('match reminder','Match Reminder'),('captain report', "Captain's Report")])
    dia = IntegerField('Days in advance', validators=[InputRequired()])
    rem_id = HiddenField('')
    delete_reminder = BooleanField('Delete')

class ReminderSetForm(FlaskForm):
    reminders = FieldList(FormField(ReminderForm))

    add_btn = SubmitField('+')
    rem_btn = SubmitField('Delete')
    submit_reminder = SubmitField('Submit')

    def load_reminders(self):
        rems = ReminderSettings.query.order_by(ReminderSettings.category).all()

        for i,r in enumerate(rems):
            self.reminders.append_entry()
            self.reminders[i].category.data = r.category
            self.reminders[i].dia.data = r.days_in_advance
            self.reminders[i].rem_id.data = r.id
        return

class NewsForm(FlaskForm):
    content = PageDownField('Enter your post using markdown')
    submit_new = SubmitField('Submit')
    submit_edit = SubmitField('Edit Post')
    submit_delete = SubmitField('Delete Post')



