from flask import Flask, g, render_template, request, redirect
from datetime import datetime, time
import pyrebase
import re
app = Flask(__name__)


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


firebase = pyrebase.initialize_app(config)
db = firebase.database()

idlist = ["Not Exist"]
searchlist = []


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    try:
        if request.method == 'POST':
            fname = request.form['fname'].lower()
            mname = request.form['mname'].lower()
            lname = request.form['lname'].lower()
            mb = request.form['mb']
            title = (fname[0]+mname[0]+lname[0] +
                     "-" + mb[-3] + mb[-2]+mb[-1]).upper()
            idlist.append(title)
            if(title != "" and len(mb) != 0):

                db.child(title).child("").set(
                    {'First  Name': fname, 'Middle Name': mname, 'Last   Name': lname, 'Mobile     ': mb})

            return render_template('index.html', id_display=idlist[-1])
        return render_template('index.html', id_display=idlist[-1])

    except:

        return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        data = []
        if request.method == 'POST':
            id = request.form['id'].upper()
            searchlist.append(id)
            data = db.child(id).child("").get().val().values()
            return render_template('search.html', data=data)
        return render_template('search.html', data=data)
    except:
        return render_template('search.html')


@app.route('/update', methods=['GET', 'POST'])
def update():
    try:
        id = searchlist[-1]
        data = db.child(id).child("").get().val().values()
        data = list(data)
        temp = []
        for i in data:
            temp.append(i)
        db.child(id).remove()
        return render_template('update.html', fname=temp[0], mname=temp[1], lname=temp[2], mb=temp[3])
    except:
        return render_template('alert.html')


if __name__ == "__main__":
    app.run(debug=True, port=8000)
