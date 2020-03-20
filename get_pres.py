from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField, SelectField
from wtforms.validators import DataRequired
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thequickbrownfrog'

import jinja2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thequickbrownfrog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

##*****************************************##
## Connect to your local postgres database ##
##*****************************************##

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:astuart@localhost/president'


db = SQLAlchemy(app)
bootstrap = Bootstrap(app)


class SearchButton_Form(FlaskForm):
    submit = SubmitField('Go To Search')


class NameForm(FlaskForm):
    name2 = RadioField('Search by First or Last Name:', choices=[('first_name', 'First Name'), ('last_name', 'Last Name')])
    name1 = StringField('Enter a name:', validators=[DataRequired()])
    name3 = SelectField('Limit results by:', choices=[('1', '1'), ('5', '5'), ('10', '10'),('50', '50')])
    name4 = SelectField('Order results by:', choices=[('first_name', 
            'First Name'), ('last_name', 'Last Name'), ('city', 'City of Birth')])
    submit = SubmitField('Submit')


class Data(db.Model):
    __tablename__ = "president"
    id = db.Column(db.Integer,
                        primary_key=True,
                        autoincrement=True)
    last_name = db.Column(db.String(15),
                        index=False,
                        nullable=False)
    first_name = db.Column(db.String(15),
                        index=False,
                        nullable=False)
    suffix = db.Column(db.String(5),
                        index=False,
                        nullable=True)
    city = db.Column(db.String(20),
                        index=False,
                        nullable=False)
    state = db.Column(db.String(2),
                        index=False,
                        nullable=False)
    birth = db.Column(db.DateTime,
                        index=False,
                        nullable=False)
    death = db.Column(db.DateTime,
                        index=False,
                        nullable=True)

    def __init__(self, last_name, first_name, suffix, city, state, birth, death):
        self.last_name = last_name
        self.first_name = first_name
        self.suffix = suffix
        self.city = city
        self.state = state
        self.birth = birth
        self.death = death

    def __repr__(self):
        return f"<President {self.last_name}>"


@app.route("/", methods =['GET','POST'])
def index():
    form2 = SearchButton_Form()
    if request.method == 'POST':
        return redirect('/search')
    return render_template("index.html", form2=form2)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/ref')
def ref():
    return render_template('ref.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route("/results", methods = ['GET', 'POST'])
def presults():
    name1 = session.get('name1')
    name2 = session.get('name2')
    name3 = session.get('name3')
    name4 = session.get('name4')
    form3 = SearchButton_Form()

    searchterm = "%{}%".format(name1) ## adds % wildcards to front & back of search term
    displayorder = eval('Data.{}'.format(name4))

    if name2 == 'last_name':
        presults = Data.query.filter(Data.last_name.like(searchterm)).order_by(displayorder).limit(name3).all()
    else:  ##  if not last_name defaults to first_name
        presults = Data.query.filter(Data.first_name.like(searchterm)).order_by(displayorder).limit(name3).all()

    #presults = Data.query.all()
    #presults = Data.query.order_by(Data.first_name).all()
    #presults = Data.query.filter(Data.last_name == name1).order_by(Data.last_name).all()
    #presults = Data.query.filter_by(Data.last_name.like(searchterm)).order_by(displayorder).all()

    if request.method == 'POST':
        return redirect('/search')

    return render_template('pres_results.html', presults=presults,\
     name1=name1,name2=name2,name3=name3,name4=name4,form3=form3)


@app.route('/search', methods=['GET', 'POST'])
def search():
    name1 = None
    name2 = None
    name3 = None
    name4 = None
    form = NameForm()
    if form.validate_on_submit():
        if request.method == 'POST':
           session['name1']  = form.name1.data		# name1 is search term entered in first text box on form
           session['name2']  = form.name2.data		# name2 is to specify first or last name in search query
           session['name3']  = form.name3.data		# name3 is to limit the number of results displayed in table
           session['name4']  = form.name4.data		# name4 is to specify the order of the search results
#          return '''<h1>The name1 value is: {}</h1>
#                  <h1>The name2  value is: {}</h1>'''.format(name1, name2)
           return redirect('/results')

        form.name1.data = ''	## Reset form values
        form.name2.data = ''
        form.name3.data = ''
        form.name4.data = ''
    return render_template('search.html', form=form) 

if __name__ == "__main__":
    app.run(debug=True)

