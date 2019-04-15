from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, PasswordField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import Required, Email, Length, EqualTo, NumberRange

class LoginForm(FlaskForm):
    email = TextField('Email', validators=[Required()])
    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('Remember_me', default=False)
    submit = SubmitField('Log in')
    
class SignUpForm(FlaskForm):
    user_name = TextField('user name', validators=[
        Required(), Length(max=20)])
    user_email = TextField('user email', validators=[
        Email(), Required(), Length(max=128)])
    password = PasswordField('password', validators=[Required(),EqualTo('password2',message='Passwords must match!')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Sign up')
    
class AboutMeForm(FlaskForm):
    describe = TextAreaField('about me', validators=[
        Required(), Length(max=200)])
    submit = SubmitField('YES!')

class AgeForm(FlaskForm):
    age = IntegerField(validators=[Required(),NumberRange(0,100,'age should be 0-100')])
    submit = SubmitField('YES!')

class CommentForm(FlaskForm):
    content= TextAreaField('content', validators=[
        Required(), Length(max=300)])
    submit = SubmitField('Publish')

class PublishBlogForm(FlaskForm):
    title = TextAreaField('blog title', validators=[Required()])
    content = TextAreaField('blog content', validators=[Required()])
    label = TextAreaField('label', render_kw={"placeholder": "split by ;"})
    #category = SelectMultipleField('category', choices=[])
    submit = SubmitField('Submit')
    