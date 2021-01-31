import secrets
import os
from flask import render_template, url_for, flash, redirect, request
from werkzeug.utils import secure_filename
from webapp import app
from webapp import APP_TITLE
from webapp import APP_VERSION
from webapp.forms import XmlMainForm, XmlUploadForm
from webapp.models import User, Post
import webapp.xmlparser as XPars


@app.route("/")
@app.route("/home")
def home():

    print("rendering template")

    return render_template("home.html", app_title=APP_TITLE, title="Home Page")
    print("rendered template")


@app.route("/about")
def about():

    return render_template(
        "about.html", app_title=APP_TITLE, app_version=APP_VERSION, title="About"
    )


@app.route("/xmlparser/upl", methods=["GET", "POST"])
def xmlparserupl():
    form = XmlUploadForm()
    if form.validate_on_submit():
        # print(f'INSTANCE PATH: {app.instance_path}')
        # print(f'ROOT PATH: {app.root_path}')
        file_dir = os.path.join(app.root_path, "uploads")
        file_name = form.sourcefile.data
        sec_file_name = secure_filename(file_name.filename)
        file_name.save(os.path.join(file_dir, sec_file_name))
        flash("File uploaded successfully!", "success")
        return redirect(url_for("xmlparsermain"))

    return render_template(
        "xmlparserupl.html", app_title=APP_TITLE, title="XML Parser", form=form
    )


@app.route("/xmlparser/main", methods=["GET", "POST"])
def xmlparsermain():
    form = XmlMainForm()
    btn_pressed = 0
    if form.validate_on_submit():
        attr_option = form.attributehandling.data
        if request.method == "POST":
            form_data = request.form
            print(form_data)

        if form.loadfile.data:
            btn_pressed = 1
            msg = [
                "This is the my message and it is a long one. I hope there are better solutions for asfjlkfdö jjksfad jsdaf fölasdfjöl fasdlkj asdlködsf asdfklj",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fadsöllsjdlk fsaddsfalkj fdsaöl jksfdlkjsdf",
                "sadflkjöasfd jdsfaljk dfas.",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fadsöllsjdlk fsaddsfalkj fdsaöl jksfdlkjsdf",
                "sadflkjöasfd jdsfaljk dfas.",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fadsöllsjdlk fsaddsfalkj fdsaöl jksfdlkjsdf",
                "sadflkjöasfd jdsfaljk dfas.",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fadsöllsjdlk fsaddsfalkj fdsaöl jksfdlkjsdf",
                "sadflkjöasfd jdsfaljk dfas.",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fadsöllsjdlk fsaddsfalkj fdsaöl jksfdlkjsdf",
                "sadflkjöasfd jdsfaljk dfas.",
                "fasdöjfdsalkjsfd lösadj lds jsadflkö dsfalöj adsflöjadsf lkdsaf ldsjk asdlkf asdölf jdsa",
                "fadsöllsjdlk fsaddsfalkj fdsaöl jksfdlkjsdf",
                "sadflkjöasfd jdsfaljk dfas.",
            ]

            for line in msg:
                flash(line, "load_summary")

        elif form.inspectfile.data:
            btn_pressed = 2
            msg = []
            for line in msg:
                flash(line, "inspect_text")

        elif form.buildexcel.data:
            btn_pressed = 3

        flash(
            f"attribute handling option chosen: {attr_option}, button pressed was: {btn_pressed}",
            "info",
        )

        return redirect(url_for("xmlparsermain"))

    return render_template(
        "xmlparsermain.html", app_title=APP_TITLE, title="XML Parser", form=form
    )
