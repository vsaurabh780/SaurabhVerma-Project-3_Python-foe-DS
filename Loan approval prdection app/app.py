from flask import Flask, request, render_template, redirect, url_for, session
from flask_bcrypt import Bcrypt

import pickle
import numpy as np
import sklearn
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'home_loan'
 
mysql = MySQL(app)

model = pickle.load(open('model_loan.pkl','rb'))

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route("/login", methods = ['POST','GET'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s AND password = % s', (username, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username'] 
            msg = 'Logged in successfully !'
            return render_template('predict.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = % s', (username, ))
        user = cursor.fetchone()
        if user:
            msg = 'Account already exists !'
        elif not username or not password:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO users VALUES (NULL, % s, % s)', (username, password))
            mysql.connection.commit()
            msg = 'Your account was registered successfully !'
            return render_template('login.html', msg = msg)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))

@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        Gender=int(request.form['gender'])
        Married=int(request.form['married'])
        Dependents=float(request.form['dependents'])
        Education=int(request.form['education'])
        Self_Employed=int(request.form['self_employed'])
        Applicantincome=int(request.form['applicant_income'])
        Coapplicantincome=float(request.form['coapplicant_income'])        
        Loan_Amount=float(request.form['loan_amount'])
        Loan_Term=float(request.form['loan_term'])
        Credit_History=int(request.form['credit_history'])
        Property_Area=int(request.form['property_area'])
        
        prediction=model.predict([[Gender,Married,Dependents,Education,Self_Employed,Applicantincome,Coapplicantincome,Loan_Amount,Loan_Term,Credit_History,Property_Area]])
        if prediction[0] >= 0.50:
            ptext="Congrats!!! You are eligible for the Loan"
        else:
            ptext="Sorry!!! Not eligible for the loan"
        
        #output=prediction[0]
        return render_template('predict.html',prediction_text=ptext) #"Your Loan Eligibility is {}%".format(output))
    
if __name__=="__main__":
    app.run(debug=True)