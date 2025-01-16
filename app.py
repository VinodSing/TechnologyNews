# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
import pymysql
import re

app = Flask(__name__)

app.secret_key = 'your secret key'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '12345678'
app.config['MYSQL_DATABASE_DB'] = 'technews'

# mysql = MySQL(app)
mysql = MySQL(cursorclass=pymysql.cursors.DictCursor)
mysql.init_app(app)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/techno')
def techno():
	return render_template('techno.html')

@app.route('/crypto')
def crypto():
	return render_template('crypto.html')

@app.route('/stock')
def stock():
	return render_template('stock.html')

@app.route('/updatenews')
def updatenews():
	return render_template('updatenews.html')

@app.route('/addnews', methods =['GET', 'POST'])
def addnews():
	msg = ''
	if request.method == 'POST' and 'email' in request.form and 'heading' in request.form and 'subheading' in request.form and 'content' in request.form:
		email = request.form['email']
		heading = request.form['heading']
		subheading = request.form['subheading']
		content = request.form['content']
		# create cursor object
		cursor = mysql.get_db().cursor()
		cursor.execute('SELECT * FROM usernews WHERE email = % s and heading = % s', (email, heading, ))
		temp = cursor.fetchone()
		if temp:
			msg = 'News ALready exist !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', heading):
			msg = 'heading must contain only characters and numbers !'
		else:
			cursor.execute('INSERT INTO usernews VALUES (NULL, % s, % s, % s, % s)', (email, heading, subheading, content, ))
			mysql.connection.commit()
			msg = 'News has been successfullully sent for validation!'
			return render_template('addnews.html', msg = msg)
	elif request.method == 'POST':
		msg = 'Please fill out the details !'
	return render_template('addnews.html', msg = msg)

@app.route('/updatingnews', methods = ['GET', 'POST'])
def updatingnews():
	msg = ""
	if 'loggedin' in session:
		if request.method == 'POST' and 'email' in request.form and 'heading' in request.form and 'subheading' in request.form and 'content' in request.form:
			email = request.form['email']
			heading = request.form['heading']
			subheading = request.form['subheading']
			content = request.form['content']
			# create cursor object
			cursor = mysql.get_db().cursor()
			cursor.execute('SELECT * FROM usernews  WHERE email = % s', (email, ))
			account = cursor.fetchone()
			cursor.execute('UPDATE usernews SET heading = %s, subheading = %s, content = %s WHERE email = %s', (heading, subheading, content, (session['email'], ), ))
			mysql.connection.commit()
			msg = 'News successfully updated !'
		elif request.method == 'POST':
			msg = 'Please fill out the news !'
		return render_template("updatingnews.html", msg = msg)
	return redirect(url_for('signin'))
          
@app.route('/signin', methods =['GET', 'POST'])
def signin():
	msg = ''
	if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
		email = request.form['email']
		password = request.form['password']
		# create cursor object
		cursor = mysql.get_db().cursor()
		cursor.execute('SELECT * FROM register WHERE email = % s AND password = % s', (email, password, ))
		account = cursor.fetchone()
		if account:
			session['loggedin'] = True
			session['email'] = account['email']
			msg = 'Logged in successfully !'
			return render_template('mainaccountpage.html', msg = msg)
		else:
			msg = 'Incorrect username / password !'
	return render_template('signin.html', msg = msg)

@app.route('/logout')
def logout():
 session.pop('loggedin', None)
 session.pop('email', None)
 return redirect(url_for('signin'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'contact' in request.form:
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		contact = request.form['contact']
		# create cursor object
		cursor = mysql.get_db().cursor()
		cursor.execute('SELECT * FROM register WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'name must contain only characters and numbers !'
		else:
			cursor.execute('INSERT INTO register VALUES (NULL, % s, % s, % s, % s)', (username, password, email, contact, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
			return render_template('register.html', msg = msg)
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)



@app.route('/displaynews', methods =['GET', 'POST'])
def displaynews():
	msg = ''
	if 'loggedin' in session:
		if request.method == 'POST' and 'email' in request.form:
			email = request.form['email']
			# create cursor object
			cursor = mysql.get_db().cursor()
			cursor.execute('SELECT * FROM usernews WHERE email = % s', (session['email'], ))
			account = cursor.fetchone()
			return render_template("displaynews.html", account=account)
		return redirect(url_for('signin'))

@app.route('/delete', methods = ['GET', 'POST'])
def delete():
	if 'loggedin' in session:
		if request.method == 'POST' and 'email' in request.form:
			email = request.form['email']
			# create cursor object
			cursor = mysql.get_db().cursor()
			cursor.execute('DELETE FROM usernews WHERE email = % s', (session['email'], ))
			mysql.connection.commit()
			return render_template("mainaccountpage.html")
		return render_template("delete.html")

if __name__ == '__main__':
	app.run(host ="localhost", port=8000, debug=True)
