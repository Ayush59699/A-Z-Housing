from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField,FileField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    fullname = StringField('Fullname', validators=[DataRequired(), Length(min=3, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=35)])
    address=StringField("Address", validators=[DataRequired(), Length(max=80)])
    pincode=IntegerField("Pincode", validators=[DataRequired()])
    submit = SubmitField('Register')


class ProfessionalSignupForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=80)])
    service_name=SelectField("Service Name", choices=[
        ('','Select'),
        ('A.C. Repair',"A.C. Repair"),
        ('Saloon','Saloon'),
        ('cooking','Cooking'),
        ('cleaning','Cleaning'),
        ('Gardening','Gardening')
    ])
    experience = IntegerField('Experience (in years)', validators=[DataRequired()])
    document = FileField('Attach Document', validators=[DataRequired()])  # For document attachment
    address = StringField('Address', validators=[DataRequired(), Length(max=200)])
    pincode = IntegerField('Pincode', validators=[DataRequired()])
    submit = SubmitField('Register')


class ServiceForm(FlaskForm):
    name = StringField('Service Name', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    submit = SubmitField('Add Service')
