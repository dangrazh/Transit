import secrets
import os
from flask import render_template, url_for, flash, redirect
from webapp import app
from webapp import APP_TITLE
from webapp import APP_VERSION
from webapp.forms import RegistrationForm, LoginForm, XmlBaseForm
from webapp.models import User, Post



@app.route("/")
@app.route("/home")
def home():
	print("rendering template")
	return render_template('home.html', app_title=APP_TITLE, title='Home Page')
	print("rendered template")

@app.route("/about")
def about():

	return render_template('about.html', app_title=APP_TITLE, app_version=APP_VERSION, title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', app_title=APP_TITLE, title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', app_title=APP_TITLE, title='Login', form=form)



def upload_sourcefile(form_sourcefile):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_sourcefile.filename)
    sourcefile_fn = random_hex + f_ext
    sourcefile_path = os.path.join(app.root_path, 'static/xml_files', sourcefile_fn)

    # output_size = (125, 125)
    # i = Image.open(form_sourcefile)
    # i.thumbnail(output_size)
    # i.save(sourcefile_path)
    # §§§ build upload logic for standard file §§§

    return sourcefile_fn


@app.route("/xmlparserupl", methods=['GET', 'POST'])
def xmlparserupl():
    form = XmlBaseForm()
    if form.validate_on_submit():
        flash('validate_on_submit true!', 'success')
        return redirect(url_for('xmlparserupl'))
    else:
        flash('validate on submit false!', 'success')
    

    return render_template('xmlparser.html', app_title=APP_TITLE, title='XML Parser', form=form) 

