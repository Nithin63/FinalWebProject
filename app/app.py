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

   @app.route('/', methods=['GET'])
def index():
    user = {'username': 'House Project'}
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow')
    result = cursor.fetchall()
    return render_template('index.html', title='Home', user=user, homes=result, template_folder='templates')


@app.route('/view/<int:home_id>', methods=['GET'])
def record_view(home_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow WHERE id=%s', home_id)
    result = cursor.fetchall()
    return render_template('view.html', title='View Form', home=result[0])


@app.route('/edit/<int:home_id>', methods=['GET'])
def form_edit_get(home_id):
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow WHERE id=%s', home_id)
    result = cursor.fetchall()
    return render_template('edit.html', title='Edit Form', home=result[0])


@app.route('/edit/<int:home_id>', methods=['POST'])
def form_update_post(city_id):
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('fldIndex'), request.form.get('fldLivingSpacesqr'), request.form.get('fldBeds'),
                 request.form.get('fldBaths'), request.form.get('fldZip'),
                 request.form.get('fldYear'), request.form.get('fldListPrice'), home_id)
    sql_update_query = """UPDATE zillow templates SET templates.fldIndex = %s, templates.fldLivingSpacesqr = %s, templates.fldBeds = %s, templates.fldBaths = 
    %s, templates.fldZip = %s, templates.fldYear = %s, templates.fldListPrice = %s WHERE templates.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/homes/new', methods=['GET'])
def form_insert_get():
    return render_template('new.html', title='New Home Form')


@app.route('/homes/new', methods=['POST'])
def form_insert_post():
    cursor = mysql.get_db().cursor()
    inputData = (request.form.get('fldIndex'), request.form.get('fldLivingSpacesqr'), request.form.get('fldBeds'),
                 request.form.get('fldBaths'), request.form.get('fldZip'),
                 request.form.get('fldYear'), request.form.get('fldListPrice'))
    sql_insert_query = """INSERT INTO zillow (fldIndex,fldLivingSpacesqr,fldBeds,fldBaths,fldZip,fldYear,fldListPrice) VALUES (%s, %s,%s, %s,%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/delete/<int:home_id>', methods=['POST'])
def form_delete_post(home_id):
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM zillow WHERE id = %s """
    cursor.execute(sql_delete_query, home_id)
    mysql.get_db().commit()
    return redirect("/", code=302)


@app.route('/api/v1/homes', methods=['GET'])
def api_browse() -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow')
    result = cursor.fetchall()
    json_result = json.dumps(result)
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/homes/<int:home_id>', methods=['GET'])
def api_retrieve(home_id) -> str:
    cursor = mysql.get_db().cursor()
    cursor.execute('SELECT * FROM zillow WHERE id=%s', home_id)
    result = cursor.fetchall()
    json_result = json.dumps(result);
    resp = Response(json_result, status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/homes/<int:home_id>', methods=['PUT'])
def api_edit(home_id) -> str:
    cursor = mysql.get_db().cursor()
    content = request.json
    inputData = (content['fldIndex'], content['fldLivingSpacesqr'], content['fldBeds'],
                 content['fldBaths'], content['fldZip'],
                 content['fldYear'], content['fldListPrice'], home_id)
    sql_update_query = """UPDATE zillow templates SET templates.fldIndex = %s, templates.fldLivingSpacesqr = %s, templates.fldBeds = %s, templates.fldBaths = 
        %s, templates.fldZip = %s, templates.fldYear = %s, templates.fldListPrice = %s WHERE templates.id = %s """
    cursor.execute(sql_update_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp


@app.route('/api/v1/homes', methods=['POST'])
def api_add() -> str:
    content = request.json

    cursor = mysql.get_db().cursor()
    inputData = (content['fldIndex'], content['fldLivingSpacesqr'], content['fldBeds'],
                 content['fldBaths'], content['fldZip'],
                 content['fldYear'], request.form.get('fldListPrice'))
    sql_insert_query = """INSERT INTO zillow (fldIndex,fldLivingSpacesqr,fldBeds,fldBaths,fldZip,fldYear,fldListPrice) VALUES (%s, %s,%s, %s,%s, %s,%s) """
    cursor.execute(sql_insert_query, inputData)
    mysql.get_db().commit()
    resp = Response(status=201, mimetype='application/json')
    return resp


@app.route('/api/v1/homes/<int:home_id>', methods=['DELETE'])
def api_delete(home_id) -> str:
    cursor = mysql.get_db().cursor()
    sql_delete_query = """DELETE FROM zillow WHERE id = %s """
    cursor.execute(sql_delete_query, home_id)
    mysql.get_db().commit()
    resp = Response(status=200, mimetype='application/json')
    return resp

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
