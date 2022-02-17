
from flask import Flask, render_template, g, request, session, redirect, url_for
import pyrebase
import datetime
import pytz
import os
from twilio.rest import Client
import random


app = Flask(__name__)

app.secret_key = os.urandom(24)

config = {
    "apiKey": "AIzaSyDBSF5dBTeK0dn--nN-_XUuOWHo7hkGEt4",
    "authDomain": "opticals-data.firebaseapp.com",
    "databaseURL": "https://opticals-data-default-rtdb.firebaseio.com",
    "projectId": "opticals-data",
    "storageBucket": "opticals-data.appspot.com",
    "messagingSenderId": "560114777981",
    "appId": "1:560114777981:web:fa35eee353d96998eb9614",
    "measurementId": "G-V8BYKQZ0LK"

}
# Firebase Connection
firebase = pyrebase.initialize_app(config)
db = firebase.database()


# Global Declarations
flag = 0  # update is there or not
idlist = ["Not Exist"]  # ID/Mobile history
globalid = ""  # To avoid ID/Mobile Conflicts
otp = 0  # OTP Config

# IST Time Regulating
IST = pytz.timezone('Asia/Kolkata')


# Twilio Pkg For OTP
account_sid = 'AC96bc5f875f483cd30e965fb3fa30e545'
auth_token = 'c193862f66f6f5717d510902268e7f58'
client = Client(account_sid, auth_token)

# index Template


@app.route('/', methods=['GET', 'POST'])
def sendotp():
    global otp
    try:
        if request.method == 'POST':
            mb = request.form['username'].casefold()
            session['user'] = request.form['username'].upper()
            if(mb == "parth".casefold() or mb == "urvisha".casefold() or mb == "admin".casefold()):
                otp = getotpapi("+91"+mb)
                return render_template('index2.html', mb="Registered Mobile Number", otp=otp)
            else:
                return render_template('alert.html', alert="You are not Valid User", type="danger", times=2, rlink="/dropsession")

        return render_template('index.html')
    except:
        return render_template('index.html')

# OTP Template


@app.route('/index2', methods=['GET', 'POST'])
def index2():
    global otp, loginflag
    try:
        if request.method == 'POST':
            session['password'] = request.form['password']
            if session['password'] == str(otp):
                return redirect(url_for("dashboard", user=session['user']))
        return render_template('alert.html', alert="Wrong OTP, Enter Relogin", type="danger", times=2, rlink="/dropsession")
    except Exception as e:
        return render_template('alert.html', alert="Unable Proceed, Enter Again", type="danger", times=2, rlink="/dropsession")

# OTP Sending & Generation


def getotpapi(mb):
    global otp
    otp = random.randint(1000, 9999)
    #client.messages.create(body=f"Your OTP is {otp}", from_="+18304453967", to=mb)
    return otp

# Dashboard Template


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    try:
        if g.user:
            return render_template('dashboard.html', user=session['user'])
        return redirect(url_for('index'))
    except:
        return render_template('alert.html', alert="Some Error Occurred !!! Pls Try Again", type="danger", times=2, rlink="/dropsession")

# Session['User'] Management


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

# Dropsession


@app.route('/dropsession')
def dropsesion():
    session.pop('user', None)
    return render_template('index.html')


# Add Template
@app.route('/add', methods=['GET', 'POST'])
def add():
    global flag, idlist, globalid, loginflag
    try:
        if session['user']:
            if (flag):
                fname = request.form['fname'].lower()
                lname = request.form['lname'].lower()
                mb = request.form['mb']

                id = flag[0:10]
                child1 = flag[11:]
                if(id != "" and len(mb) != 0 and id == mb):
                    db.child(id).child(child1).update(
                        {'First Name': fname,  'Last Name': lname, 'Mobile': str(mb), 'ydata': str(id) + " " + child1})
                    globalid = id
                    idlist.append(globalid)
                if(id != mb):
                    db.child(id).child(child1).remove()
                    if(id != "" and len(mb) != 0):
                        db.child(mb).child(child1).set(
                            {'First Name': fname,  'Last Name': lname, 'Mobile': str(mb), 'ydata': str(mb)+" "+child1})
                        globalid = mb
                        idlist.append(globalid)

                flag = 0
                return render_template('add.html', lc=idlist[-1])

            if request.method == 'POST' and flag == 0:
                fname = request.form['fname'].lower()
                lname = request.form['lname'].lower()
                mb = request.form['mb']
                current_time = datetime.datetime.now(IST)
                title = mb
                child1 = str(current_time.day) + "-" + str(current_time.month) + "-" + str(current_time.year) + \
                    " " + str(current_time.hour) + ":" + \
                    str(current_time.minute) + ":" + \
                    str(current_time.second)

                if(title != "" and len(mb) != 0):
                    db.child(title).child(child1).set(
                        {'First Name': fname,  'Last Name': lname, 'Mobile': str(mb), 'ydata': str(mb)+" "+child1})
                    globalid = mb
                    idlist.append(globalid)
                return render_template('alert.html', alert="Entry Recorded Sucessfully!!!", lc=idlist[-1], type="success", times=2, rlink="/add")

            return render_template('add.html', lc=idlist[-1], position="sticky")
        else:
            return render_template('alert.html', alert="Error occured, Try Again", type="danger", times=2, rlink="/dropsession")

    except:
        return render_template('alert.html', alert="Entry Not Recorded", type="danger", times=4, rlink="/add")

# Search Template


@app.route('/search', methods=['GET', 'POST'])
def search():
    data = []
    try:
        if session['user']:

            if request.method == 'POST':
                id = request.form['id'].upper()
                data = db.child(id).child("").get().val().values()
                data = list(data)
                if(data):
                    return render_template('search.html', data=data, position="fixed")

            return render_template('search.html', data=data, position="sticky")
        else:
            return render_template('alert.html', alert="Error occured, Try Again", type="danger", times=2, rlink="/dropsession")
    except:
        return render_template('alert.html', alert="Pls try once Again, Not Found", type="danger", times=4, rlink="/search")

# Update Template


@app.route('/update/<string:ydata>', methods=['GET', 'POST'])
def update(ydata):
    try:
        if session['user']:

            id = ydata[0:10]
            child1 = ydata[11:]
            data = db.child(id).child(child1).get().val()
            data = dict(data)

            global flag
            flag = ydata
            return render_template('update.html', fname=data['First Name'], lname=data['Last Name'], mb=data['Mobile'])
        else:
            return render_template('alert.html', alert="Error occured, Try Again", type="danger", times=2, rlink="/dropsession")

    except:
        return render_template('alert.html', alert="Not Updated,Try Aagin", type="danger", times=4, rlink="/search")

# Delete Config


@app.route('/delete/<string:ydata>', methods=['GET', 'POST'])
def delete(ydata):
    try:
        if session['user']:
            id = ydata[0:10]
            child1 = ydata[11:]
            if(id != "" and len(child1) != 0):
                db.child(id).child(child1).remove()
            return render_template('alert.html', alert="Sucessfully Deleted!!!!", type="success", times=2, rlink="/add")
        else:
            return render_template('alert.html', alert="Entry not deleted, Try Again", type="danger", times=2, rlink="/dropsession")

    except:
        return render_template('alert.html', alert="Not Successful, Try Again. Thank you", type="danger", times=4, rlink="/add")

# Sales Template


@app.route('/sales', methods=['GET', 'POST'])
def sales():
    try:
        if session['user']:
            return render_template('sales.html', position="fixed")
        else:
            return render_template('alert.html', alert="Error occured, Try Again", type="danger", times=2, rlink="/dropsession")
    except:
        return render_template('alert.html', alert="Unable to Fetch!!!!", type="danger", times=4, rlink="/add")


# Main Method
if __name__ == "__main__":
    app.run(debug=True, port=5000)
