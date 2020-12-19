from typing import List, Dict
import simplejson as json
import mysql.connector
from flask import Flask, request, Response, redirect, url_for
from flask import render_template
import os
from dotenv import load_dotenv
from flask_oidc import OpenIDConnect
from oauth2client.client import OAuth2Credentials

load_dotenv()

app = Flask(__name__)
user = {'username': 'Wenbo Wang'}

app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'OIDC_CLIENT_SECRETS': './client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_SCOPES': ["openid", "profile", "email"],
    'OIDC_CALLBACK_ROUTE': '/authorization-code/callback'
})
oidc = OpenIDConnect(app)

class MyDb:
    def __init__(self):
        self.config = {
            'user': 'root',
            'password': 'root',
            'host': 'db',
            'port': '3306',
            'database': 'deniroData'
        }

    def connect(self):
        self.connection = mysql.connector.connect(** self.config)

    def closeDb(self):
        self.connection.close()

    def get_alldata(self):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM deniro')
        data = cursor.fetchall()
        self.closeDb()
        return data

    def get_rating(self, rating_id):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM deniro WHERE id=%s', (rating_id,))
        result = cursor.fetchall()
        data = result[0]
        self.closeDb()
        return data

    def update_rating(self, inputData):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        sql_update_query = """UPDATE deniro t SET t.Year = %s, t.Score = %s, t.Title = %s WHERE t.id = %s """
        cursor.execute(sql_update_query, inputData)
        self.connection.commit()
        self.closeDb()

    def insert_rating(self, inputData):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        sql_insert_query = """INSERT INTO deniro (`Year`,Score,Title) VALUES (%s, %s, %s) """
        cursor.execute(sql_insert_query, inputData)
        self.connection.commit()
        self.closeDb()

    def delete_rating(self, rating_id):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        sql_delete_query = """DELETE FROM deniro WHERE id = %s """
        cursor.execute(sql_delete_query, (rating_id,))
        self.connection.commit()
        self.closeDb()

    def insert_calendar(self, inputData):
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        sql_insert_query = """INSERT INTO calendar (`UserEmail`,Events) VALUES (%s, %s) """
        print(sql_insert_query , "123")
        cursor.execute(sql_insert_query, inputData)
        self.connection.commit()
        self.closeDb()

db = MyDb()


@app.route('/')
def index():
    deniro = db.get_alldata()
    info = oidc.user_getinfo(["sub", "name", "email"]) if oidc.user_loggedin else None
    return render_template('index.html', title='Home', user=user, deniro=deniro, profile=info, oidc=oidc)

@app.route("/login")
@oidc.require_login
def login():
    return redirect("/")

@app.route("/logout", methods=["POST"])
def logout():
    oidc.logout()
    return redirect("/")


@app.route('/view/<int:rating_id>', methods=['GET'])
def record_view(rating_id):
    info = oidc.user_getinfo(["sub", "name", "email"]) if oidc.user_loggedin else None
    rating = db.get_rating(rating_id)
    return render_template('view.html', title='View Form', user=user, rating=rating, profile=info, oidc=oidc)


@app.route('/edit/<int:rating_id>', methods=['GET'])
def form_edit_get(rating_id):
    rating = db.get_rating(rating_id)
    info = oidc.user_getinfo(["sub", "name", "email"]) if oidc.user_loggedin else None
    return render_template('edit.html', title='Edit Form', user=user, rating=rating, profile=info, oidc=oidc)


@app.route('/edit/<int:rating_id>', methods=['POST'])
def form_update_post(rating_id):
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'), rating_id)
    db.update_rating(inputData)
    return redirect("/", code=302)

@app.route('/rating/new', methods=['GET'])
def form_insert_get():
    info = oidc.user_getinfo(["sub", "name", "email"]) if oidc.user_loggedin else None
    return render_template('new.html', title='New Rating Form', user=user, profile=info, oidc=oidc)


@app.route('/rating/new', methods=['POST'])
def form_insert_post():
    inputData = (request.form.get('Year'), request.form.get('Score'), request.form.get('Title'))
    db.insert_rating(inputData)
    return redirect("/", code=302)

@app.route('/delete/<int:rating_id>', methods=['POST'])
def form_delete_post(rating_id):
    db.delete_rating(rating_id)
    return redirect("/", code=302)

@app.route('/calendar', methods=['GET'])
def calendar():
    CLIENT_ID=os.getenv('CLIENT_ID')
    API_KEY=os.getenv('API_KEY')
    info = oidc.user_getinfo(["sub", "name", "email"]) if oidc.user_loggedin else None
    return render_template('calendar.html', title='Calendar', user=user, CLIENT_ID=CLIENT_ID, API_KEY=API_KEY, profile=info, oidc=oidc)


# API v1

@app.route('/api/v1/ratings')
def api_ratings() -> str:
    js = json.dumps(db.get_alldata())
    resp = Response(js, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/ratings/<int:rating_id>', methods=['GET'])
def api_retrieve(rating_id) -> str:
    result = db.get_rating(rating_id)
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp

@app.route('/api/v1/ratings/', methods=['POST'])
def api_add() -> str:
    content = request.json
    inputData = (content['Year'], content['Score'], content['Title'])
    db.insert_rating(inputData)
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/ratings/<int:rating_id>', methods=['PUT'])
def api_edit(rating_id) -> str:
    content = request.json
    inputData = (content['Year'], content['Score'], content['Title'], rating_id)
    db.update_rating(inputData)
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/ratings/<int:rating_id>', methods=['DELETE'])
def api_delete(rating_id) -> str:
    db.delete_rating(rating_id)
    resp = Response(status=210, mimetype='application/json')
    return resp

@app.route('/api/v1/calendar', methods=['POST'])
def api_calendar() -> str:
    content = request.json
    inputData = (content['email'], json.dumps(content['events']))
    db.insert_calendar(inputData)
    resp = Response(status=200, mimetype='application/json')
    return resp



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) # set debug=False on deployment