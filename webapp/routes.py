import re
import secrets
import os
from flask import (
    render_template,
    url_for,
    flash,
    redirect,
    send_from_directory,
    session,
)  # ,  request
from werkzeug.utils import secure_filename

from webapp import app
from webapp import APP_TITLE, APP_VERSION, APP_AUTHOR

from webapp.forms import (
    XmlFileDetailForm,
    XmlMainForm,
    XmlSummaryForm,
    XmlUploadForm,
)

from webapp.xmlparser import AttributeUsage
from webapp.fileprocessor import FileProcessor


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", app_title=APP_TITLE, title="Home Page")


@app.route("/about")
def about():
    return render_template(
        "about.html",
        app_title=APP_TITLE,
        app_version=APP_VERSION,
        app_author=APP_AUTHOR,
        title="About",
    )


@app.route("/xmlparser/upload", methods=["GET", "POST"])
def xmlparserupload():
    form = XmlUploadForm()
    if form.validate_on_submit():
        # print(f'INSTANCE PATH: {app.instance_path}')
        # print(f'ROOT PATH: {app.root_path}')
        file_dir = os.path.join(app.root_path, "uploads")
        try:
            file_name = form.sourcefile.data
            sec_file_name = secure_filename(file_name.filename)
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'filename'":
                flash("Please select a file to be uploaded!", "danger")
            else:
                flash("{e}", "danger")
            return redirect(url_for("xmlparserupload"))

        file_name.save(os.path.join(file_dir, sec_file_name))

        # process the file
        fp = FileProcessor(os.path.join(file_dir, sec_file_name))
        session["FileProcessor"] = fp

        flash("File uploaded successfully!", "success")
        return redirect(url_for("xmlparserfilesummary"))

    return render_template(
        "xmlparserupload.html", app_title=APP_TITLE, title="XML Parser", form=form
    )


@app.route("/xmlparser/filesummary", methods=["GET", "POST"])
def xmlparserfilesummary():
    form = XmlSummaryForm()
    fp = session["FileProcessor"]
    if form.validate_on_submit():
        if form.btn_details.data:
            return redirect(url_for("xmlparserdetails"))
        elif form.btn_next.data:
            return redirect(url_for("xmlparsermain"))

    return render_template(
        "xmlparserfilesummary.html",
        app_title=APP_TITLE,
        title="XML Parser",
        form=form,
        fp=fp,
    )


@app.route("/xmlparser/filedetails", methods=["GET", "POST"])
def xmlparserdetails():
    form = XmlFileDetailForm()
    new_var = session["FileProcessor"]
    fp = new_var

    if form.validate_on_submit():
        if form.btn_cancel.data:
            return redirect(url_for("home"))
        elif form.btn_next.data:
            return redirect(url_for("xmlparsermain"))

    return render_template(
        "xmlparserfiledetails.html",
        app_title=APP_TITLE,
        title="XML Parser",
        form=form,
        fp=fp,
    )


@app.route("/xmlparser/main", methods=["GET", "POST"])
def xmlparsermain():
    form = XmlMainForm()
    new_var = session["FileProcessor"]
    fp = new_var
    samples = {}
    # parsed = False

    if form.validate_on_submit():
        # if request.method == "POST":
        #     form_data = request.form
        #     print(form_data)

        if form.inspectfile.data:
            # get the attribute usage setting and do the actual processing of the file
            attr_option = form.attributehandling.data
            if attr_option == 1:
                ret_val = fp.process_file(
                    attribute_usage=AttributeUsage.add_separate_tag
                )
            elif attr_option == 2:
                ret_val = fp.process_file(
                    attribute_usage=AttributeUsage.add_to_tag_name
                )
            elif attr_option == 3:
                ret_val = fp.process_file(
                    attribute_usage=AttributeUsage.add_to_tag_value
                )
            elif attr_option == 4:
                ret_val = fp.process_file(attribute_usage=AttributeUsage.ignore)
            else:
                # default to option 1
                ret_val = fp.process_file(
                    attribute_usage=AttributeUsage.add_separate_tag
                )

            # set the parsed flag
            # parsed = True

            # store the parsed fp objet in the session
            session["FileProcessor"] = fp

            # check if file was parsed without errors/warnings
            if ret_val == "success":
                # get the samples
                samples = fp.inspect_samples()

                return render_template(
                    "xmlparsermain.html",
                    app_title=APP_TITLE,
                    title="XML Parser",
                    form=form,
                    fp=fp,
                    samples=samples,
                    # parsed=parsed,
                )
            else:
                flash("Parsing the file resulted in errors or warnings!", "danger")
                return redirect(url_for("xmlparserdetails"))

        elif form.buildexcel.data:
            file_dir = os.path.join(app.root_path, "results")

            # get the fp object from the session
            fp = session["FileProcessor"]
            gen_excel_result = fp.to_excel(file_dir)
            if "No output data extracted" in gen_excel_result:
                flash(gen_excel_result, "danger")
                return redirect(url_for("xmlparsermain"))
            else:
                # flash(gen_excel_result, "success")
                return send_from_directory(
                    directory=file_dir, filename=gen_excel_result, as_attachment=True
                )

    return render_template(
        "xmlparsermain.html",
        app_title=APP_TITLE,
        title="XML Parser",
        form=form,
        fp=fp,
        samples=samples,
        # parsed=parsed,
    )
