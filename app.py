from flask import Flask, g, render_template, request
import pyrebase
import datetime

from sqlalchemy import false, null
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

flag = 0
firebase = pyrebase.initialize_app(config)
db = firebase.database()

#idlist = ["Not Exist"]
searchlist = []


@app.route('/', methods=['GET', 'POST'])
def hello_world():
    global flag
    if (flag):
        fname = request.form['fname'].lower()
        mname = request.form['mname'].lower()
        lname = request.form['lname'].lower()
        mb = request.form['mb']
        id = flag[0:10]
        child1 = flag[10:]
        if(id != "" and len(mb) != 0):
            db.child(id).child(child1).update(
                {'First Name': fname, 'Middle Name': mname, 'Last Name': lname, 'Mobile': str(mb)})
        flag = 0
        return render_template('index.html')
    try:

        if request.method == 'POST' and flag == 0:
            fname = request.form['fname'].lower()
            mname = request.form['mname'].lower()
            lname = request.form['lname'].lower()
            mb = request.form['mb']
            # title = (fname[0]+mname[0]+lname[0] +
            # +8"-" + mb[-3] + mb[-2]+mb[-1]).upper()
            current_time = datetime.datetime.now()
            title = mb
            child1 = str(current_time.day) + "-" + str(current_time.month) + "-" + str(current_time.year) + \
                " " + str(current_time.hour) + ":" + \
                str(current_time.minute) + ":" + str(current_time.second)
            # idlist.append(title)

            if(title != "" and len(mb) != 0):
                db.child(title).child(child1).set(
                    {'First Name': fname, 'Middle Name': mname, 'Last Name': lname, 'Mobile': str(mb), 'ydata': str(mb)+child1})

            return render_template('index.html')

        return render_template('index.html')

    except:

        return render_template('alert.html')


@app.route('/search', methods=['GET', 'POST'])
def search():
    try:
        data = []
        if request.method == 'POST':
            id = request.form['id'].upper()
            searchlist.append(id)
            data = db.child(id).child("").get().val().values()
            data = list(data)
            return render_template('search.html', data=data)
        return render_template('search.html', data=data)
    except:
        return render_template('search.html')


@app.route('/update/<string:ydata>', methods=['GET', 'POST'])
def update(ydata):
    try:
        #id = searchlist[-1]
        id = ydata[0:10]
        child1 = ydata[10:]

        data = db.child(id).child(child1).get().val()
        data = dict(data)

        #temp = []
        # for i in data:
        # temp.append(i)
        global flag
        flag = ydata
        # db.child(id).remove()
        return render_template('update.html', fname=data['First Name'], lname=data['Last Name'], mname=data['Middle Name'], mb=data['Mobile'])

    except:
        return render_template('alert.html')


if __name__ == "__main__":
    app.run(debug=True, port=8000)
