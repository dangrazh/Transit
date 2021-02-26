from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    TextAreaField,
    RadioField,
)
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms_components import read_only


class XmlUploadForm(FlaskForm):
    sourcefile = FileField(
        "Upload source file", validators=[FileAllowed(["txt", "xml"])]
    )
    btn_submit = SubmitField("Upload")


class XmlSummaryForm(FlaskForm):
    btn_details = SubmitField("Full Details")
    btn_next = SubmitField("Next")


class XmlFileDetailForm(FlaskForm):
    btn_next = SubmitField("Next")
    btn_cancel = SubmitField("Cancel")


class XmlMainForm(FlaskForm):
    attributehandling = RadioField(
        "Please choose one of the options to handle attributes:",
        choices=[
            (1, "Create separate Tag  "),
            (2, "Add to Tag  "),
            (3, "Add to Value  "),
            (4, "Ignore Attributes  "),
        ],
        default=1,
        coerce=int,
    )
    inspectfile = SubmitField("Inspect file")
    buildexcel = SubmitField("Create Excel")
    summary = TextAreaField("File summary")
    output = TextAreaField("Inspect Result")

    def __init__(self, *args, **kwargs):
        super(XmlMainForm, self).__init__(*args, **kwargs)
        read_only(self.summary)
        read_only(self.output)


class TabTest(FlaskForm):
    btn_next = SubmitField("Next")