from flask import request, redirect, render_template, flash, url_for, escape
from album_app import app, db, bcrypt
from album_app.forms import RegistrationForm, LoginForm, PostForm
from album_app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import album_app.photo_analyse
from album_app.log_sys import log_request


@app.route('/')
def welcome():
    return render_template('welcome.html', web_title="欢迎")


@app.route('/intro')
def intro():
    return render_template('introduction.html', web_title="功能介绍")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # 已登陆直接跳转回主页
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('register_success'))
    return render_template('register.html', form=form, web_title="注册")


@app.route('/success')
def register_success():
    return render_template('register_success.html', web_title="注册成功")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))  # 已登陆直接跳转回主页
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')  # 跳转回此前目标访问页面
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('登陆失败，请检查邮箱和密码。', 'danger')
    return render_template('login.html', form=form, web_title="登陆")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('welcome'))


@app.route('/explore')
def explore():
    posts = Post.query.order_by(Post.date_posted.desc()).all()  # 按日期排序
    return render_template('explore.html', posts=posts, web_title="探索")


@app.route('/home')
@login_required
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()  # 按日期排序
    return render_template('home.html', posts=posts, web_title="主页")


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = PostForm()
    if form.validate_on_submit():
        the_tag = album_app.photo_analyse.photo_tag(form.url.data)
        log_request(request, the_tag)
        post = Post(title=form.title.data, details=form.details.data, url=form.url.data, author=current_user, tag=the_tag)
        db.session.add(post)
        db.session.commit()
        flash('你的图片已上传成功！', 'success')
        return redirect(url_for('upload'))
    return render_template('upload.html', form=form, web_title="上传")


@app.route("/account")
@login_required
def account():
    account_posts = Post.query.order_by(Post.date_posted.desc()).filter_by(author=current_user)
    return render_template('account.html', posts=account_posts, web_title='我')


@app.route('/log')
def view_the_log():
    contents = []
    with open('photo_analyse.log', 'r') as log:
        for line in log:
            contents.append([])
            for item in line.split('|'):
                contents[-1].append(escape(item))
    titles = ('用户输入数据', '远程地址', '用户代理', '分析结果')
    return render_template('log.html',
                           web_title='查看日志',
                           the_row_titles=titles,
                           the_data=contents,)
