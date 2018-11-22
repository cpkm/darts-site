from flask import render_template, flash, redirect, url_for, request, current_app, g
from flask_login import current_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime
from app import db
from app.main import bp
#from app.main.forms import EditProfileForm, PostForm, SearchForm
from app.models import Player, Game, Match, Team


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

@bp.route('/player')
@login_required
def player():
    return 0

@bp.route('/match')
@login_required
def match():
    return 0

@bp.route('/team')
@login_required
def team():
    return 0

@bp.route('/search')
@login_required
def search():
    return 0