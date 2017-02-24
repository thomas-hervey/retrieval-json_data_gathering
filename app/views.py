from flask import render_template, flash, redirect, session, url_for, request, g
from flask_login import login_user, logout_user, current_user, \
    login_required
from datetime import datetime
from app import app, db, lm, oid
from .forms import LoginForm, EditForm, SearchForm
from .models import User, Search, Data
from config import POSTS_PER_PAGE


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated:
        g.user.last_seen = datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()


@app.errorhandler(403)
def page_not_found(e):
    app.logger.error('Permission Denied: %s %s', request.path, e)
    return render_template('404.html'), 404


@app.errorhandler(404)
def page_not_found(e):
    app.logger.error('Page not found: %s %s', request.path, e)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    app.logger.error('Internal Error: %s %s', request.path, e)
    return render_template('500.html'), 500


# @app.errorhandler(Exception)
# def unhandled_exception(e):
#     app.logger.error('Unhandled Exception: %s', e)
#     return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/index/<int:page>', methods=['GET', 'POST'])
@login_required
def index(page=1):
    form = SearchForm()  # set form to data search form
    if form.validate_on_submit():  # if submission is valid
        flash('Form submission was valid')  # TODO: remove
        # create and add search result
        search = Search(form)  # create source result
        search.author = g.user
        db.session.add(search)
        db.session.commit()

        return redirect(url_for('user', nickname=g.user.nickname))
    return render_template('index.html',
                           form=form)


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for=['nickname', 'email'])
    return render_template('login.html',
                           title='Sign In',
                           form=form,
                           providers=app.config['OPENID_PROVIDERS'])


@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    this_user = User.query.filter_by(email=resp.email).first()
    if this_user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        this_user = User(nickname=nickname, email=resp.email)
        db.session.add(this_user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(this_user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/user/<nickname>')
@app.route('/user/<nickname>/<int:page>')
@login_required
def user(nickname, page=1):
    this_user = User.query.filter_by(nickname=nickname).first()
    if this_user is None:
        flash('User %s not found.' % nickname)
        return redirect(url_for('index'))
    searches = this_user.searches.paginate(page, POSTS_PER_PAGE, False)
    return render_template('user.html',
                           user=this_user,
                           search=searches)


@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        db.session.add(g.user)
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    elif request.method != "POST":
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
                           form=form)


@app.route('/delete/<int:id>')
@login_required
def delete(id):
    this_search = Search.query.get(id)
    if this_search is None:
        flash('Result not found.')
        return redirect(url_for('index'))
    if this_search.author.id != g.user.id:
        flash('You cannot delete this search result.')
        return redirect(url_for('index'))
    db.session.delete(this_search)
    db.session.commit()
    flash('Your search result has been deleted.')
    print "Deleted search with ID: ", this_search.id
    
    # if associated data exists
    if Data.query.get(id):
        this_search_data = Data.query.get(id)
        # delete data too
        if this_search.id == this_search_data.id:
            db.session.delete(this_search_data)
            db.session.commit()
            print "Deleted data with ID: ", this_search_data.id
        else:
            print "Could query Data with ID: ", id, " but doesn't match search ID: ", this_search.id, " so not deleted"
    else:
        print "no associated data to be deleted"
    
    return redirect(url_for('user',
                            nickname=g.user.nickname))


@app.route('/create/<int:id>')
@login_required
def create(id):
    this_search = Search.query.get(id)
    if this_search is None:
        flash('Result not found.')
        return redirect(url_for('index'))
    if this_search.author.id != g.user.id:
        flash('You cannot explore data from this search.')
        return redirect(url_for('index'))

    data = Data(this_search)
    data.id = this_search.id  # make search & data ID the same
    data.source = this_search  # set data.source relationship
    db.session.add(data)
    db.session.commit()
    if data.id != this_search.id:
        flash("Search ID and Data ID do not match, so it will be deleted")
        print this_search.id, data.id
        this_data = Data.query.filter_by(id=data.id).first()
        db.session.delete(this_data.id)
        
    print "Created Data with ID: ", data.id
    print "Data type: ", data.data_type
    return redirect(url_for('user',
                            nickname=g.user.nickname))


@app.route('/explore/<int:id>')
@login_required
def explore(id):
    this_search = Search.query.get(id)
    if this_search is None:
        flash('Result not found.')
        return redirect(url_for('index'))
    if this_search.author.id != g.user.id:
        flash('You cannot explore data from this search.')
        return redirect(url_for('index'))
    
    this_data = Data.query.get(id)
    if this_data.id != this_search.id:
        flash("Search ID and Data ID do not match")
        print this_search.id, this_data.id
        return redirect(url_for('index'))

    print "Exploring Data with ID: ", this_data.id
    # return redirect(url_for('explore',
    #                         data=this_data))
    return render_template('explore.html',
                           data=this_data)

@app.route('/delete_data/')
@login_required
def delete_data():
    datas = Data.query.all()
    for data in datas:
        db.session.delete(data)
        db.session.commit()
    flash('All data elements have been deleted')
    return redirect(url_for('explore',
                            nickname=g.user.nickname))
                    
                    # ,
                    #         nickname=g.user.nickname,
                    #         data=data)
