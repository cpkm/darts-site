from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from wtforms.validators import ValidationError
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from datetime import datetime, date
from app import db, schedules
from app.main import bp
from app.main.forms import (EditPlayerForm, EditTeamForm, EditMatchForm, EnterScoresForm, HLScoreForm, RosterForm,
    ClaimPlayerForm, EditSeasonForm)
from app.models import (User, Player, Game, Match, Team, PlayerGame, PlayerSeasonStats, Season,
    season_from_date, update_all_team_stats, current_roster, current_season)
from app.decorators import check_verification, check_role
from app.main.leaderboard_card import LeaderBoardCard
from app.main.email import send_reminder_email as reminder_email

@bp.before_request
def before_request():
    g.all_seasons = Season.query.order_by(Season.start_date.desc()).all()


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
def index():
    all_players = Player.query.filter_by(is_active=True).order_by(Player.nickname).all()
    page = request.args.get('page', 1, type=int)
    last_match = Match.query.filter(Match.date<date.today()).order_by(Match.date.desc()).first()
    schedule = Match.query.filter(Match.date>=date.today()).order_by(Match.date).paginate(
        page, current_app.config['MATCH_PER_PAGE'], False)
    next_url = url_for('main.index', page=schedule.next_num) \
        if schedule.has_next else None
    prev_url = url_for('main.index', page=schedule.prev_num) \
        if schedule.has_prev else None

    leader_board_list = [ 
        LeaderBoardCard('Stars',PlayerSeasonStats.query.join(Player).\
            filter(PlayerSeasonStats.season==current_season()).\
            with_entities(Player.nickname,PlayerSeasonStats.total_stars).\
            order_by(PlayerSeasonStats.total_stars.desc()).limit(4).all()),
        LeaderBoardCard('High Scores',PlayerSeasonStats.query.join(Player).\
            filter(PlayerSeasonStats.season==current_season()).\
            with_entities(Player.nickname,PlayerSeasonStats.total_high_scores).\
            order_by(PlayerSeasonStats.total_high_scores.desc()).limit(4).all()),
        LeaderBoardCard('Low Scores',PlayerSeasonStats.query.join(Player).\
            filter(PlayerSeasonStats.season==current_season()).\
            with_entities(Player.nickname,PlayerSeasonStats.total_low_scores).\
            order_by(PlayerSeasonStats.total_low_scores.desc()).limit(4).all()) ]

    return render_template('index.html', title=None,
        schedule=schedule.items, next_url=next_url, prev_url=prev_url, 
        all_players=all_players, last_match=last_match,leader_board_list=leader_board_list)


@bp.route('/player_edit',  methods=['GET', 'POST'], defaults={'nickname': None})
@bp.route('/player_edit/<nickname>',  methods=['GET', 'POST'])
@login_required
@check_verification
@check_role(['admin','captain'])
def player_edit(nickname):
    player = Player.query.filter_by(nickname=nickname).first()
    form = EditPlayerForm(nickname)
    all_players = Player.query.order_by(Player.nickname).all()
    
    if form.submit_new.data and form.validate():
        newplayer = Player(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            nickname=form.nickname.data,
            tagline=form.tagline.data)
        if Player.query.filter_by(nickname=newplayer.nickname).first() is None:
            db.session.add(newplayer)
            db.session.flush()
            player_id = newplayer.id
            db.session.commit()
            player = Player.query.filter_by(id=player_id).first()
            player.create_checkins()

            flash('Player {} ({} {}) added!'.format(
                newplayer.nickname, newplayer.first_name, newplayer.last_name))
            return redirect(url_for('main.player_edit'))
        flash('Player {} ({} {}) already exists!'.format(
            newplayer.nickname, newplayer.first_name, newplayer.last_name), 'warning')

    if form.submit_edit.data and form.validate() and player is not None:
        player.first_name = form.first_name.data
        player.last_name = form.last_name.data
        player.nickname = form.nickname.data
        player.tagline = form.tagline.data
        db.session.add(player)
        db.session.commit()
        flash('Player {} ({} {}) modified!'.format(
            player.nickname, player.first_name, player.last_name))
        return redirect(url_for('main.player_edit', nickname=player.nickname))

    if  form.submit_delete.data and player is not None:
        player.destroy_checkins()
        stats=PlayerSeasonStats.query.filter_by(player=player).all()
        for m in [player]+stats:
            db.session.delete(m)
        db.session.commit()
        flash('Player {} ({} {}) and all associated stats deleted!'.format(
            player.nickname, player.first_name, player.last_name), 'danger')
        return redirect(url_for('main.player_edit'))

    elif request.method == 'GET' and player is not None:
        form.first_name.data = player.first_name
        form.last_name.data = player.last_name
        form.nickname.data = player.nickname
        form.tagline.data = player.tagline

    return render_template('edit_player.html', title='Player Editor', 
        form=form, player=player, all_players=all_players)


@bp.route('/team_edit',  methods=['GET', 'POST'], defaults={'name': None})
@bp.route('/team_edit/<name>',  methods=['GET', 'POST'])
@login_required
@check_verification
@check_role(['admin','captain'])
def team_edit(name):
    team = Team.query.filter_by(name=name).first()
    form = EditTeamForm(obj=team)
    all_teams = Team.query.order_by(Team.name).all()
    
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
@check_verification
@check_role(['admin','captain'])
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
        newmatch.set_season()
        db.session.add(newmatch)
        db.session.flush()
        match_id = newmatch.id
        db.session.commit()
        match = Match.query.filter_by(id=match_id).first()
        match.create_checkins()

        flash('Match {} {} {} added!'.format(newmatch.date, form.opponent.data, form.home_away.data))
        return redirect(url_for('main.match_edit'))

    if form.submit_edit.data and form.validate() and match is not None:
        match.date = form.date.data
        match.opponent = Team.query.filter_by(name=form.opponent.data).first()
        match.home_away = form.home_away.data
        match.match_type = form.match_type.data
        match.set_location()
        match.set_season()
        db.session.add(match)
        db.session.commit()

        for p in match.get_roster():
            p.update_activity()

        flash('Match {} {} {} modified!'.format(form.date.data, form.opponent.data, form.home_away.data))
        return redirect(url_for('main.match_edit', id=match.id))

    if  form.submit_delete.data and match is not None:
        match_season = match.season
        match_roster = match.get_roster()
        match.delete_all_games()
        match.destroy_checkins()

        db.session.delete(match)
        db.session.commit()

        for p in match_roster:
            p.update_player_stats(season=match_season)
            p.update_activity()

        flash('Match {} {} {} and all associated games deleted!'.format(form.date.data, form.opponent.data, form.home_away.data), 'danger')
        return redirect(url_for('main.match_edit'))

    if request.method=='GET' and match is not None:
        form.load_match(match)

    return render_template('edit_match.html', title='Match Editor', 
        form=form, match=match, all_matches=all_matches)

@bp.route('/season_edit',  methods=['GET', 'POST'], defaults={'id': None})
@bp.route('/season_edit/<id>',  methods=['GET', 'POST'])
@login_required
@check_verification
@check_role(['admin','captain'])
def season_edit(id):
    season = Season.query.filter_by(id=id).first()
    form = EditSeasonForm(season=season)

    all_seasons = Season.query.order_by(Season.start_date.desc()).all()

    if form.submit_new.data and form.validate():
        new_season = Season(season_name=form.season_name.data,
            start_date=form.start_date.data, end_date=form.end_date.data)
        db.session.add(new_season)
        db.session.commit()

        for m in Match.query.all():
            m.set_season()
            db.session.add(m)
            db.session.commit()

        for p in Player.query.all():
            p.update_player_stats(season='all')

        flash('Season {} added and matches updated!'.format(new_season.season_name))
        return redirect(url_for('main.season_edit'))

    if form.submit_edit.data and form.validate() and season is not None:
        season.season_name = form.season_name.data
        season.start_date = form.start_date.data
        season.end_date = form.end_date.data
        db.session.add(season)
        db.session.commit()

        for m in Match.query.all():
            m.set_season()
            db.session.add(m)
            db.session.commit()

        for p in Player.query.all():
            p.update_player_stats(season='all')

        flash('Season {} updated!'.format(season.season_name))
        return redirect(url_for('main.season_edit',id=season.id))

    if  form.submit_delete.data and season is not None:
        db.session.delete(season)
        db.session.commit()

        for m in Match.query.all():
            m.set_season()
            db.session.add(m)
            db.session.commit()

        for p in Player.query.all():
            p.update_player_stats(season='all')

        flash('Season {} deleted!'.format(season.season_name), 'danger')
        return redirect(url_for('main.season_edit'))

    if request.method=='GET' and season is not None:
        form.load_season(season)

    return render_template('edit_season.html', title='Season Editor', 
        form=form, season=season, all_seasons=all_seasons)


@bp.route('/enter_score',  methods=['GET', 'POST'], defaults={'id': None})
@bp.route('/enter_score/<id>',  methods=['GET', 'POST'])
@login_required
@check_verification
@check_role(['admin','captain','assistant'])
def enter_score(id):
    match = Match.query.filter_by(id=id).first()
    form = EnterScoresForm(obj=match)
    all_seasons = Season.query.order_by(Season.start_date.desc()).all()
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

        for p in Player.query.all():
            p.update_player_stats(season=match.season)

        flash('Match {} {} {} details edited!'.format(match.date.strftime('%Y-%m-%d'), match.opponent.name, match.home_away))
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

        for p in Player.query.all():
            p.update_player_stats(season=match.season)
            p.update_activity()

        update_all_team_stats()
        match.update_match_stats()
        flash('Match {} {} {} scores entered successfully!'.format(match.date.strftime('%Y-%m-%d'), match.opponent.name, match.home_away), 'success')
        return redirect(url_for('main.enter_score', id=match.id))

    if hl_form.add_btn.data:
        new_row = hl_form.hl_scores.append_entry()
        new_row.player.choices = [(p.nickname,p.nickname) for p in Player.query.all()]

        return render_template('enter_score.html', title='Enter Scores', 
        form=form, hl_form=hl_form, match=match)

    if hl_form.rem_btn.data:
        hl_form.hl_scores.pop_entry()
        return render_template('enter_score.html', title='Enter Scores', 
        form=form, hl_form=hl_form, match=match)

    if hl_form.submit_hl_scores.data and match is not None:

        print(hl_form.validate())
        for fieldName, errorMessages in hl_form.errors.items():
            for err in errorMessages:
                print(err)

        match.delete_all_books()
        hl_form.save_scores(match)

        for p in match.get_roster():
            p.update_player_stats(season=match.season)
            p.update_activity()

        update_all_team_stats()
        flash('Match {} {} {} high/low scores entered successfully!'.format(match.date.strftime('%Y-%m-%d'), match.opponent.name, match.home_away), 'success')
        return redirect(url_for('main.enter_score', id=match.id))

    if request.method=='GET' and match is not None:
        form.load_games(match)
        hl_form.load_scores(match)

    if request.method=='POST' and match is not None:
        form.load_games(match)
        hl_form.load_scores(match)

    return render_template('enter_score.html', title='Enter Scores', 
        form=form, hl_form=hl_form, match=match, all_seasons=all_seasons)


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
        season = current_season()
    else:
        season = Season.query.filter_by(id=id).first_or_404()
    all_seasons = Season.query.order_by(Season.start_date.desc()).all()
    matches = Match.query.filter_by(season=season).order_by(Match.date).all()
    return render_template('schedule.html', season=season, matches=matches, all_seasons=all_seasons)

@bp.route('/opponent',  methods=['GET', 'POST'], defaults={'id': None})
@bp.route('/opponent/<id>',  methods=['GET', 'POST'])
def opponent(id):
    opponent = Team.query.filter_by(id=id).first()
    matches = Match.query.filter_by(opponent=opponent).order_by(Match.date).all()
    all_teams = Team.query.order_by(Team.name).all()
    return render_template('opponent.html', opponent=opponent, all_teams=all_teams, matches=matches)

@bp.route('/match/<id>',  methods=['GET', 'POST'])
def match(id):
    match = Match.query.filter_by(id=id).first_or_404()
    roster = match.get_roster()
    return render_template('match.html', match=match, roster=roster)

@bp.route('/leaderboard',  methods=['GET', 'POST'], defaults={'year_str':'all time'})
@bp.route('/leaderboard/',  methods=['GET', 'POST'], defaults={'year_str':'all time'})
@bp.route('/leaderboard/<year_str>',  methods=['GET', 'POST'])
def leaderboard(year_str):
    try:
        board = request.args['board']
    except:
        board=None
        pass

    roster = Player.query.filter(~Player.nickname.in_(['Dummy','Sub'])).all()

    if year_str.lower() == 'all time':
        stats = [sum(PlayerSeasonStats.query.join(Player).filter(Player.nickname==p.nickname).all()) for p in roster] 
    else:
        if year_str == 'current':
            year_str = current_season().season_name
        elif year_str == 'last':
            year_str = current_season(last=1).season_name
        else:
            year_str = year_str.replace('-','/') # This is to allow date name to be 'url-friendly'
        stats = PlayerSeasonStats.query.join(Season).filter_by(season_name=year_str).\
            join(Player).filter(Player.nickname.in_([p.nickname for p in roster])).all()
    return render_template('leaderboard.html', roster=roster, stats=stats, year_str=year_str, board=board)

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.player:
        nickname = current_user.player.nickname
        player = Player.query.filter_by(nickname=nickname).first()
        checked_matches = player.checked_matches_association.\
            join(Match).filter(Match.date>=date.today()).order_by(Match.date).all()
    else:
        player = None
        nickname = None
        checked_matches = None

    player_form = EditPlayerForm(nickname)
    claim_form = ClaimPlayerForm()

    if request.method=='POST' and claim_form.submit_claim.data and claim_form.validate():
        claimed_player = Player.query.filter_by(nickname=claim_form.player.data).first()

        if not claimed_player:
            flash('Please select a player to claim.', 'danger')
            return redirect(url_for('main.profile'))
            
        current_user.player = claimed_player
        db.session.add(current_user)
        db.session.commit()

        flash('Player {} ({} {}) claimed!'.format(
            claimed_player.nickname, claimed_player.first_name, claimed_player.last_name))
        return redirect(url_for('main.profile'))

    if request.method=='POST' and player_form.submit_new.data and player_form.validate():
        new_player = Player(nickname=player_form.nickname.data,
            first_name=player_form.first_name.data,
            last_name=player_form.last_name.data)

        db.session.add(new_player)
        db.session.commit()

        current_user.player = Player.query.filter_by(nickname=new_player.nickname).first()
        db.session.add(current_user)
        db.session.commit()

        flash('Player {} ({} {}) assigned!'.format(
            new_player.nickname, new_player.first_name, new_player.last_name))
        return redirect(url_for('main.profile'))

    if request.method=='POST' and player_form.submit_edit.data and player_form.validate() and player is not None:
        player.first_name = player_form.first_name.data
        player.last_name = player_form.last_name.data
        player.nickname = player_form.nickname.data
        player.tagline = player_form.tagline.data
        db.session.add(player)
        db.session.commit()
        flash('Player {} ({} {}) modified!'.format(
            player.nickname, player.first_name, player.last_name))
        return redirect(url_for('main.profile'))

    elif request.method == 'GET' and player is not None:
        player_form.first_name.data = player.first_name
        player_form.last_name.data = player.last_name
        player_form.nickname.data = player.nickname
        player_form.tagline.data = player.tagline

    return render_template('profile.html', player_form=player_form, claim_form=claim_form, 
        checked_matches=checked_matches)


@bp.route('/captain', methods=['GET', 'POST'])
@login_required
@check_verification
@check_role(['admin','captain'])
def captain():
    roster_form = RosterForm()
    players = current_roster(full=True)

    if request.method == 'POST' and roster_form.validate_on_submit():
        for player_form in roster_form.roster:
            if player_form.player.data is not None:
                p = Player.query.filter_by(nickname=player_form.player.data).first()
                p.is_active = player_form.is_active.data
                if p.user:
                    if p.user.role == 'admin':
                        pass
                    elif current_user == p.user:
                        pass
                    else:
                        p.user.role=player_form.role.data
                        db.session.add(p.user)
                db.session.add(p)
                db.session.commit()
        flash('Updated active roster!')
        return redirect(url_for('main.captain'))

    elif request.method == 'GET':
        roster_form.fill_roster(players)

    upcoming_matches = Match.query.filter(Match.date>=date.today()).order_by(Match.date).all()

    return render_template('captain.html', roster_form=roster_form, 
        players=players, upcoming_matches=upcoming_matches)

@bp.route('/admin', methods=['GET', 'POST'])
@login_required
@check_verification
@check_role(['admin'])
def admin():
    all_users = User.query.all()
    all_players = Player.query.all()

    return render_template('admin.html', all_users=all_users, all_players=all_players)



@bp.route('/send_reminder_email/<match_id>/<token>', methods=['GET','POST'])
@login_required
@check_verification
@check_role(['admin','captain'])
def send_reminder_email(match_id, token):
    user = User.verify_user_token(token, task='send_reminder_email')
    if not user:
        return redirect(url_for('main.index'))

    match = Match.query.filter_by(id=match_id).first()
    users = [p.user for p in current_roster() if p.user is not None]
    status = [u.player.checked_matches_association.filter_by(match_id=match.id).first().status for u in users]
    
    reminder_email(users=users,match=match,status=status)
    match.reminder_email_sent = date.today()
    db.session.add(match)
    db.session.commit()
    flash('Reminder email sent!')
    return redirect(url_for('main.captain', _anchor="email"))


@bp.route('/update_checkin/<player_id>/<match_id>/<status>/<token>', methods=['GET','POST'])
def update_checkin(player_id, match_id, status, token):
    user = User.verify_user_token(token, task='checkin')
    if not user:
        flash('Invalid token', 'danger')
        return redirect(url_for('main.index'))

    player = Player.query.filter_by(id=player_id).first()
    match = Match.query.filter_by(id=match_id).first()
    player.checkin(match,status)

    flash('Thank you for checking in!', 'success')
    if current_user == user:
        return redirect(url_for('main.checkin'))
    else:
        return redirect(url_for('main.index'))


@bp.route('/checkin', methods=['GET','POST'])
@login_required
def checkin():
    if current_user.player:
        player = Player.query.filter_by(nickname=current_user.player.nickname).first()
        checked_matches = player.checked_matches_association.\
            join(Match).filter(Match.date>=date.today()).order_by(Match.date).all()
    else:
        player = None
        checked_matches = None

    return render_template('checkin.html', checked_matches=checked_matches)


@bp.route('/upload_schedule', methods=['GET','POST'])
def upload_schedule():
    if request.method=='POST' and 'schedule_file' in request.files:
        try:
            filename = schedules.save(request.files['schedule_file'])
        except:
            flash('Not allowed')
            return redirect(url_for('main.match_edit'))

        flash('Schedule saved. {}'.format(filename))
        return redirect(url_for('main.match_edit'))
    flash('Did nada')
    return redirect('main.match_edit')


@bp.route('/search')
@login_required
def search():
    return 0
