from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import db
from app.main import bp
from app.main.forms import EditPlayerForm, EditTeamForm, EditMatchForm, DoublesGameForm
from app.models import Player, Game, Match, Team
from wtforms.validators import ValidationError


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    schedule = Match.query.paginate(
        page, current_app.config['MATCH_PER_PAGE'], False)
    next_url = url_for('main.index', page=schedule.next_num) \
        if schedule.has_next else None
    prev_url = url_for('main.index', page=schedule.prev_num) \
        if schedule.has_prev else None
    return render_template('index.html', title=None, 
        schedule=schedule.items, next_url=next_url, prev_url=prev_url)


@bp.route('/player_edit',  methods=['GET', 'POST'], defaults={'nickname': None})
@bp.route('/player_edit/<nickname>',  methods=['GET', 'POST'])
def player_edit(nickname):
    player = Player.query.filter_by(nickname=nickname).first()
    form = EditPlayerForm(obj=player)
    all_players = Player.query.all()
    
    if form.submit_new.data and form.validate():
        newplayer = Player(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            nickname=form.nickname.data)
        if Player.query.filter_by(nickname=newplayer.nickname).first() is None:
            db.session.add(newplayer)
            db.session.commit()
            flash('Player {} ({} {}) added!'.format(
                newplayer.nickname, newplayer.first_name, newplayer.last_name))
            return redirect(url_for('main.player_edit'))
        flash('Player {} ({} {}) already exists!'.format(
            newplayer.nickname, newplayer.first_name, newplayer.last_name), 'warning')

    if form.submit_edit.data and form.validate() and player is not None:
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        player.nickname = form.nickname.data
        db.session.add(player)
        db.session.commit()
        flash('Player {} ({} {}) modified!'.format(
            player.nickname, player.first_name, player.last_name))
        return redirect(url_for('main.player_edit', nickname=player.nickname))

    if  form.submit_delete.data and player is not None:
        db.session.delete(player)
        db.session.commit()
        flash('Player {} ({} {}) deleted!'.format(
            player.nickname, player.first_name, player.last_name), 'danger')
        return redirect(url_for('main.player_edit'))

    return render_template('edit_player.html', title='Player Editor', 
        form=form, player=player, all_players=all_players)


@bp.route('/team_edit',  methods=['GET', 'POST'], defaults={'name': None})
@bp.route('/team_edit/<name>',  methods=['GET', 'POST'])
def team_edit(name):
    team = Team.query.filter_by(name=name).first()
    form = EditTeamForm(obj=team)
    all_teams = Team.query.all()
    
    if form.submit_new.data and form.validate():
        newteam = Team(
            name=form.name.data,
            home_location=form.home_location.data,
            address=form.address.data)
        if Team.query.filter_by(name=newteam.name).first() is None:
            db.session.add(newteam)
            db.session.commit()
            flash('Team {} added!'.format(newteam.name))
            return redirect(url_for('main.team_edit'))
        flash('Team {} already exists!'.format(newteam.name), 'warning')

    if form.submit_edit.data and form.validate() and team is not None:
        team.name = form.name.data
        team.home_location = form.home_location.data
        team.address = form.address.data
        db.session.add(team)
        db.session.commit()
        flash('Team {} modified!'.format(team.name))
        return redirect(url_for('main.team_edit', name=team.name))

    if  form.submit_delete.data and team is not None:
        db.session.delete(team)
        db.session.commit()
        flash('Team {} deleted!'.format(team.name), 'danger')
        return redirect(url_for('main.team_edit'))

    return render_template('edit_team.html', title='Team Editor', 
        form=form, team=team, all_teams=all_teams)


@bp.route('/match_edit',  methods=['GET', 'POST'], defaults={'id': None})
@bp.route('/match_edit/<id>',  methods=['GET', 'POST'])
def match_edit(id):
    match = Match.query.filter_by(id=id).first()
    form = EditMatchForm(match=match)
    all_teams = Team.query.order_by(Team.name).all()
    team_choices = [('', '-Select Opponent-')]+[(t.name,t.name) for t in all_teams]
    form.opponent.choices=team_choices
    all_matches = Match.query.order_by(Match.date).all()

    if form.submit_new.data and form.validate():
        newmatch = Match(date=form.date.data, 
            opponent=Team.query.filter_by(name=form.opponent.data).first(), home_away=form.home_away.data)
        db.session.add(newmatch)
        db.session.commit()
        flash('Match {} {} {} added!'.format(newmatch.date, form.opponent.data, form.home_away.data))
        return redirect(url_for('main.match_edit'))

    if form.submit_edit.data and form.validate() and match is not None:
        match.date = form.date.data
        match.opponent = Team.query.filter_by(name=form.opponent.data).first()
        match.home_away = form.home_away.data
        db.session.add(match)
        db.session.commit()
        flash('Match {} {} {} modified!'.format(form.date.data, form.opponent.data, form.home_away.data))
        return redirect(url_for('main.match_edit', id=match.id))
    elif request.method=='GET' and match is not None:
        form.load_match(match)

    if  form.submit_delete.data and match is not None:
        db.session.delete(match)
        db.session.commit()
        flash('Match {} {} {} deleted!'.format(form.date.data, form.opponent.data, form.home_away.data), 'danger')
        return redirect(url_for('main.match_edit'))

    return render_template('edit_match.html', title='Match Editor', 
        form=form, match=match, all_matches=all_matches)

@bp.route('/search')
@login_required
def search():
    return 0

@bp.route('/enter_score')
def enter_score():
    form = DoublesGameForm()
    roster = Player.query.all()
    player_choices = [(p.nickname,p.nickname) for p in roster]

    form.p1.choices=player_choices
    form.p2.choices=player_choices
    return render_template('enter_score.html', title='Enter Scores', form=form)





'''
@bp.route('/match_edit',  methods=['GET', 'POST'], defaults={'id': None})
@bp.route('/match_edit/<id>',  methods=['GET', 'POST'])
def match_edit(id):
    match = Match.query.filter_by(id=id).first()
    if match is not None:
        form = EditMatchForm(date=match.date, home_away=match.home_away,
                opponent=match.opponent.name)
    else:
        form = EditMatchForm()
    all_matches = Match.query.order_by(Match.date).all()
    all_teams = Team.query.order_by(Team.name).all()

    if form.submit_new.data and form.validate():
        newmatch = Match(date=form.date.data, 
            opponent=Team.query.filter_by(name=form.opponent.data).first(), home_away=form.home_away.data)
        db.session.add(newmatch)
        db.session.commit()
        flash('Match {} {} {} added!'.format(newmatch.date, form.opponent.data, form.home_away.data))
        return redirect(url_for('main.match_edit'))

    if form.submit_edit.data and form.validate() and match is not None:
        match.date = form.date.data
        match.opponent = Team.query.filter_by(name=form.opponent.data).first()
        match.home_away = form.home_away.data
        db.session.add(match)
        db.session.commit()
        flash('Match {} {} {} modified!'.format(form.date.data, form.opponent.data, form.home_away.data))
        return redirect(url_for('main.match_edit', id=match.id))

    if  form.submit_delete.data and match is not None:
        db.session.delete(match)
        db.session.commit()
        flash('Match {} {} {} deleted!'.format(form.date.data, form.opponent.data, form.home_away.data), 'danger')
        return redirect(url_for('main.match_edit'))

    return render_template('edit_match.html', title='Match Editor', 
        form=form, match=match, all_teams=all_teams, all_matches=all_matches)
        '''