import sqlite3
import datetime
from flask import Flask,render_template, g, request, redirect, url_for

PATH='db/jobs.sqlite'

app = Flask(__name__)

def open_connection():
	connection = getattr(g,'_connection',None)
	if connection == None:
		connection = g._connection = sqlite3.connect(PATH)
	connection.row_factory = sqlite3.Row
	return connection

def execute_sql(sql,values=(),commit=False,single=False):
	connection = open_connection()
	cursor = connection.execute(sql,values)
	if commit == True:
		results = connection.commit()
	else:
		results = cursor.fetchone() if single else cursor.fetchall()

	cursor.close()
	return results

@app.teardown_appcontext
def close_connection(exception):
	connection = getattr(g,'_connection',None)
	if connection is not None:
		connection.close()


@app.route('/')
@app.route('/applications')

def applications():
	applications = execute_sql('SELECT application.id, application.title, application.description, application.details, team.id as team_id, team.name as team_name FROM application JOIN team ON team.id = application.team_id') 
	return render_template('index.html',applications=applications)

@app.route('/application/<application_id>')
def application(application_id):
	application = execute_sql('SELECT application.id, application.title, application.description, application.details, team.id as team_id, team.name as team_name FROM application JOIN team ON team.id = application.team_id WHERE application.id = ?',[application_id],single=True)
	return render_template('application.html',application=application)


@app.route('/team/<team_id>')
def team(team_id):
	team = execute_sql('SELECT * FROM team WHERE id=?',[team_id],single=True)
	applications = execute_sql('SELECT application.id, application.title, application.description, application.details FROM application JOIN team ON team.id = application.team_id WHERE team.id = ?',[team_id])
	reviews = execute_sql('SELECT review, rating, title, date, status FROM review JOIN team ON team.id = review.team_id WHERE team.id = ?',[team_id])
	return render_template('team.html',team=team,applications=applications,reviews=reviews)

@app.route('/team/<team_id>/review', methods=('GET','POST'))
def review(team_id):
	if request.method == 'POST':
		review = request.form['review']
		rating = request.form['rating']
		title = request.form['title']
		status = request.form['status']
		date = datetime.datetime.now().strftime("%m/%d/%Y")
		execute_sql('INSERT INTO review (review, rating, title, date, status, team_id) VALUES (?, ?, ?, ?, ?, ?)',(review, rating, title, date, status, team_id),commit=True)
		
		return redirect(url_for('team',team_id=team_id))
	return render_template('review.html', team_id=team_id)