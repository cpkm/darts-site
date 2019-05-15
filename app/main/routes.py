from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime, date
from app import db
from app.main import bp
from app.main.forms import EditPlayerForm, EditTeamForm, EditMatchForm, EnterScoresForm, HLScoreForm
from app.models import (User, Player, Game, Match, Team, PlayerGame, PlayerSeasonStats, Season,
    season_from_date, update_all_team_stats)
from wtforms.validators import ValidationError


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    all_players = Player.query.all()
    page = request.args.get('page', 1, type=int)
    last_match = Match.query.filter(Match.date<date.today()).order_by(Match.date.desc()).first()
    schedule = Match.query.filter(Match.date>=date.today()).order_by(Match.date).paginate(
        page, current_app.config['MATCH_PER_PAGE'], False)
    next_url = url_for('main.index', page=schedule.next_num) \
        if schedule.has_next else None
    prev_url = url_for('main.index', page=schedule.prev_num) \
		if schedule.has_prev else None
    top_stars = PlayerSeasonStats.query.join(Player).order_by(PlayerSeasonStats.total_stars.desc()).limit(4).all()
    top_high_scores = PlayerSeasonStats.query.join(Player).order_by(PlayerSeasonStats.total_high_scores.desc()).limit(4).all()
    top_low_scores = PlayerSeasonStats.query.join(Player).order_by(PlayerSeasonStats.total_low_scores.desc()).limit(4).all()

    return render_template('index.html', title=None,
        schedule=schedule.items, next_url=next_url, prev_url=prev_url, 
        all_players=all_players, last_match=last_match, top_stars=top_stars, top_high_scores=top_high_scores, top_low_scores=top_low_scores)

@bp.route('/player_edit',  methods=['GET', 'POST'], defaults={'nickname': None})
@bp.route('/player_edit/<nickname>',  methods=['GET', 'POST'])
@login_required
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
        stats=PlayerSeasonStats.query.filter_by(player=player).all()
        for m in [player]+stats:
            db.session.delete(m)
        db.session.commit()
        flash('Player {} ({} {}) and all associated stats deleted!'.format(
            player.nickname, player.first_name, player.last_name), 'danger')
        return redirect(url_for('main.player_edit'))

    return render_template('edit_player.html', title='Player Editor', 
        form=form, player=player, all_players=all_players)


@bp.route('/team_edit',  methods=['GET', 'POST'], defaults={'name': None})
@bp.route('/team_edit/<name>',  methods=['GET', 'POST'])
@login_required
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
@login_required
def match_edit(id):
    match = Match.query.filter_by(id=id).first()
    form = EditMatchForm(match=match)
    all_teams = Team.query.order_by(Team.name).all()
    team_choices = [('', '-Select Opponent-')]+[(t.name,t.name) for t in all_teams]
    form.opponent.choices=team_choices
    all_matches = Match.query.order_by(Match.date).all()

    if form.submit_new.data and form.validate():
        newmatch = Match(date=form.date.data, 
            opponent=Team.query.filter_by(name=form.opponent.data).first(), 
            home_away=form.home_away.data, match_type=form.match_type.data)
        newmatch.set_location()
        db.session.add(newmatch)
        db.session.commit()
        flash('Match {} {} {} added!'.format(newmatch.date, form.opponent.data, form.home_away.data))
        return redirect(url_for('main.match_edit'))

    if form.submit_edit.data and form.validate() and match is not None:
        match.date = form.date.data
        match.opponent = Team.query.filter_by(name=form.opponent.data).first()
        match.home_away = form.home_away.data
        match.match_type = form.match_type.data
        match.set_location()
        db.session.add(match)
        db.session.commit()
        flash('Match {} {} {} modified!'.format(form.date.data, form.opponent.data, form.home_away.data))
        return redirect(url_for('main.match_edit', id=match.id))

    if  form.submit_delete.data and match is not None:
        match.delete_all_games()
        db.session.delete(match)
        db.session.commit()
        flash('Match {} {} {} and all associated games deleted!'.format(form.date.data, form.opponent.data, form.home_away.data), 'danger')
        return redirect(url_for('main.match_edit'))

    if request.method=='GET' and match is not None:
        form.load_match(match)

    return render_template('edit_match.html', title='Match Editor', 
        form=form, match=match, all_matches=all_matches)

@bp.route('/search')
@login_required
def search():
    return 0

@bp.route('/enter_score',  methods=['GET', 'POST'], defaults={'id': None})
@bp.route('/enter_score/<id>',  methods=['GET', 'POST'])
@login_required
def enter_score(id):
    match = Match.query.filter_by(id=id).first()
    form = EnterScoresForm(obj=match)
    all_matches = Match.query.order_by(Match.date).all()
    hl_form = HLScoreForm()

    if form.submit_details.data and form.validate() and match is not None:
        match.win = form.win.data
        match.overtime = form.overtime.data
        match.team_score = form.team_score.data
        match.opponent_score = form.opponent_score.data
        match.food = form.food.data
        match.match_summary = form.match_summary.data
        db.session.add(match)
        db.session.commit()
        for p in match.get_roster():
            p.update_player_stats()
        flash('Match {} {} {} details edited!'.format(match.date, match.opponent.name, match.home_away))
        return redirect(url_for('main.enter_score', id=match.id))

     
    if form.submit_scores.data and form.validate() and match is not None:

        match.win = form.win.data
        match.overtime = form.overtime.data
        match.team_score = form.team_score.data
        match.opponent_score = form.opponent_score.data
        match.food = form.food.data
        match.match_summary = form.match_summary.data
        db.session.add(match)
        db.session.commit()

        match.delete_all_games()

        count = 1
        for j,f in enumerate(form.d701):
            i = count + j
            game = Game(match=match, win=f.win.data, game_num=i, game_type='doubles 701')
            p1 = Player.query.filter_by(nickname=f.p1.data).first()
            p2 = Player.query.filter_by(nickname=f.p2.data).first()
            pg1 = PlayerGame(player=p1, game=game, stars=int(f.p1_stars.data))
            pg2 = PlayerGame(player=p2, game=game, stars=int(f.p2_stars.data))
            db.session.add_all([game,pg1,pg2])
            db.session.commit()

        count = count + len(form.d701)
        for j,f in enumerate(form.d501):
            i = count + j
            game = Game(match=match, win=f.win.data, game_num=i, game_type='doubles 501')
            p1 = Player.query.filter_by(nickname=f.p1.data).first()
            p2 = Player.query.filter_by(nickname=f.p2.data).first()
            pg1 = PlayerGame(player=p1, game=game, stars=int(f.p1_stars.data))
            pg2 = PlayerGame(player=p2, game=game, stars=int(f.p2_stars.data))
            db.session.add_all([game,pg1,pg2])
            db.session.commit()

        count = count + len(form.d501)
        for j,f in enumerate(form.s501):
            i = count + j
            game = Game(match=match, win=f.win.data, game_num=i, game_type='singles 501')
            p1 = Player.query.filter_by(nickname=f.p1.data).first()
            pg1 = PlayerGame(player=p1, game=game, stars=int(f.p1_stars.data))
            db.session.add_all([game,pg1])
            db.session.commit()

        for p in match.get_roster():
            p.update_player_stats(match.season.season_name)
            p.update_activity()

        update_all_team_stats()
        match.update_match_stats()
        flash('Match {} {} {} scores entered successfully!'.format(match.date, match.opponent.name, match.home_away), 'success')
        return redirect(url_for('main.enter_score', id=match.id))

    if hl_form.add_btn.data:
        new_row = hl_form.hl_scores.append_entry()
        new_row.player.choices = [(p.nickname,p.nickname) for p in Player.query.all()]

        return render_template('enter_score.html', title='Enter Scores', 
        form=form, hl_form=hl_form, match=match, all_matches=all_matches)

    if hl_form.rem_btn.data:
        hl_form.hl_scores.pop_entry()
        return render_template('enter_score.html', title='Enter Scores', 
        form=form, hl_form=hl_form, match=match, all_matches=all_matches)

    if hl_form.submit_hl_scores.data and match is not None:
        match.delete_all_books()
        hl_form.save_scores(match)
        for p in match.get_roster():
            p.update_player_stats(match.season.season_name)
            p.update_activity()
        update_all_team_stats()
        flash('Match {} {} {} high/low scores entered successfully!'.format(match.date, match.opponent.name, match.home_away), 'success')
        return redirect(url_for('main.enter_score', id=match.id))

    if request.method=='GET' and match is not None:
        form.load_games(match)
        hl_form.load_scores(match)

    if request.method=='POST' and match is not None:
        form.load_games(match)
        hl_form.load_scores(match)

    return render_template('enter_score.html', title='Enter Scores', 
        form=form, hl_form=hl_form, match=match, all_matches=all_matches), print('emd')


@bp.route('/player/<nickname>',  methods=['GET', 'POST'])
def player(nickname):
    player = Player.query.filter_by(nickname=nickname).first_or_404()
    seasons = PlayerSeasonStats.query.filter_by(player_id=player.id).join(Season).order_by(Season.start_date).all()
    page = request.args.get('page', 1, type=int)
    matches = Match.query.join(Game).join(PlayerGame).filter_by(player_id=player.id).order_by(Match.date.desc()).distinct().paginate(
        page, current_app.config['MATCH_PER_PAGE'], False)
    next_url = url_for('main.player', nickname=player.nickname, page=matches.next_num) \
        if matches.has_next else None
    prev_url = url_for('main.player', nickname=player.nickname, page=matches.prev_num) \
        if matches.has_prev else None
    return render_template('player.html', next_url=next_url, prev_url=prev_url,
            player=player, matches=matches.items, seasons=seasons)


@bp.route('/schedule',  methods=['GET', 'POST'], defaults={'id': None})
@bp.route('/schedule/<id>',  methods=['GET', 'POST'])
def schedule(id):
    if id is None:
        season = season_from_date(date.today())
    else:
        season = Season.query.filter_by(id=id).first_or_404()
    all_seasons = Season.query.all()
    matches = Match.query.filter_by(season=season).order_by(Match.date).all()
    return render_template('schedule.html', season=season, matches=matches, all_seasons=all_seasons)

@bp.route('/opponent',  methods=['GET', 'POST'], defaults={'id': None})
@bp.route('/opponent/<id>',  methods=['GET', 'POST'])
def opponent(id):
    opponent = Team.query.filter_by(id=id).first()
    matches = Match.query.filter_by(opponent=opponent).order_by(Match.date).all()
    all_teams = Team.query.all()
    return render_template('opponent.html', opponent=opponent, all_teams=all_teams, matches=matches)

@bp.route('/match/<id>',  methods=['GET', 'POST'])
def match(id):
    match = Match.query.filter_by(id=id).first_or_404()
    return render_template('match.html', match=match)

@bp.route('/leaderboard',  methods=['GET', 'POST'])
def leaderboard():
    roster = Player.query.all()
    season = season_from_date(date.today())
    stats = PlayerSeasonStats.query.filter_by(season=season)
    return render_template('leaderboard.html', roster=roster, stats=stats, season=season)







