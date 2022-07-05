# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li
    :license: MIT, see LICENSE for more details.
"""
import os
try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
import geopandas as gpd
from jinja2 import escape
from jinja2.utils import generate_lorem_ipsum
from flask import Flask, make_response, request, redirect, url_for, abort, session, jsonify
# import shapefile
from json import dumps
import sqlalchemy as db
from geoalchemy2 import Geometry
# import arcpy
# import psycopg2
# import arcgisscripting

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'secret string')


user = "gis_user"
password = "GIS#p0scDb"
host = "10.70.123.125"
port = 5432
database = "tilemap"
 


# gp = arcgisscripting.create()
# conn = psycopg2.connect("dbname='tilemap' user='gis_user' host='10.70.123.125' password='GIS#p0scDb'") #connecting to DB

# cur = conn.cursor()  #setting up connection cursor
# cur.execute('''drop table thuadat''')
# cur.execute('''CREATE TABLE drugpoints
#             (gid serial primary key,
#              lo text,
#              mdsd  text,
#              dientich float,
#              congty text,
#              geom geometry);''')
# conn.commit()



    # cur.execute('''insert into thuadat(lo,mdsd,dientich,congty, geom)
    #                 values(%s,%s,%s,%s,ST_SetSRID(ST_MakePoint(%s,%s), 4269))'''
    #                 ,(lo,mdsd,dientich,congty))
    # conn.commit()


@app.route('/shp2geo')
def shp2geo():
    # reader = shapefile.Reader("data/thuadat.shp")
    # fields = reader.fields[1:]
    # field_names = [field[0] for field in fields]
    # buffer = []
    # for sr in reader.shapeRecords():
    #     atr = dict(zip(field_names, sr.record))
    #     geom = sr.shape.__geo_interface__
    #     buffer.append(dict(type="Feature", \
    #     geometry=geom, properties=atr)) 
    
    #     # write the GeoJSON file
    
    # geojson = open("pyshp-demo.json", "w")
    # geojson.write(dumps({"type": "FeatureCollection", "features": buffer}, indent=2) + "\n")
    # geojson.close()
    shp_file = gpd.read_file('data/thuadat.shp')
    shp_file.to_file('export-geo/pyshp-demo.json', driver='GeoJSON')
    return "shp2geo ok"

@app.route('/geo2shp')
def geo2shp():
    gdf = gpd.read_file('export-geo/pyshp-demo.json',encoding='utf8')
    gdf.to_file('export-shp/file.shp',encoding='utf8')

    #Read shapefile using GeoPandas
    gdf = gpd.read_file("export-shp/file.shp")
    for index, row in gdf.iterrows():
        print(index, row["geometry"])
        break

    db_connection_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    con = db.create_engine(db_connection_url)
    connection = con.connect()

    metadata = db.MetaData()


    # thuadat = db.Table('thuadat', metadata, autoload=True, autoload_with=con)

    # query = db.insert(thuadat).values( fclass='naveen', newcode=6000) 
    # ResultProxy = connection.execute(query)


    print("success")
    
    return "geo2shp ok"


# get name value from query string and cookie
@app.route('/')
@app.route('/hello')
def hello():
    name = request.args.get('name')
    if name is None:
        name = request.cookies.get('name', 'Human')
    response = '<h1>Hello, %s!</h1>' % escape(name)  # escape name to avoid XSS
    # return different response according to the user's authentication status
    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'
    return response


# redirect
@app.route('/hi')
def hi():
    return redirect(url_for('hello'))


# use int URL converter
@app.route('/goback/<int:year>')
def go_back(year):
    return 'Welcome to %d!' % (2018 - year)


# use any URL converter
@app.route('/colors/<any(blue, white, red):color>')
def three_colors(color):
    return '<p>Love is patient and kind. Love is not jealous or boastful or proud or rude.</p>'


# return error response
@app.route('/brew/<drink>')
def teapot(drink):
    if drink == 'coffee':
        abort(418)
    else:
        return 'A drop of tea.'


# 404
@app.route('/404')
def not_found():
    abort(404)


# return response with different formats
@app.route('/note', defaults={'content_type': 'text'})
@app.route('/note/<content_type>')
def note(content_type):
    content_type = content_type.lower()
    if content_type == 'text':
        body = '''Note
to: Peter
from: Jane
heading: Reminder
body: Don't forget the party!
'''
        response = make_response(body)
        response.mimetype = 'text/plain'
    elif content_type == 'html':
        body = '''<!DOCTYPE html>
<html>
<head></head>
<body>
  <h1>Note</h1>
  <p>to: Peter</p>
  <p>from: Jane</p>
  <p>heading: Reminder</p>
  <p>body: <strong>Don't forget the party!</strong></p>
</body>
</html>
'''
        response = make_response(body)
        response.mimetype = 'text/html'
    elif content_type == 'xml':
        body = '''<?xml version="1.0" encoding="UTF-8"?>
<note>
  <to>Peter</to>
  <from>Jane</from>
  <heading>Reminder</heading>
  <body>Don't forget the party!</body>
</note>
'''
        response = make_response(body)
        response.mimetype = 'application/xml'
    elif content_type == 'json':
        body = {"note": {
            "to": "Peter",
            "from": "Jane",
            "heading": "Remider",
            "body": "Don't forget the party!"
        }
        }
        response = jsonify(body)
        # equal to:
        # response = make_response(json.dumps(body))
        # response.mimetype = "application/json"
    else:
        abort(400)
    return response


# set cookie
@app.route('/set/<name>')
def set_cookie(name):
    response = make_response(redirect(url_for('hello')))
    response.set_cookie('name', name)
    return response


# log in user
@app.route('/login')
def login():
    session['logged_in'] = True
    return redirect(url_for('hello'))


# protect view
@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)
    return 'Welcome to admin page.'


# log out user
@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')
    return redirect(url_for('hello'))


# AJAX
@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)
    return '''
<h1>A very long post</h1>
<div class="body">%s</div>
<button id="load">Load More</button>
<script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
<script type="text/javascript">
$(function() {
    $('#load').click(function() {
        $.ajax({
            url: '/more',
            type: 'get',
            success: function(data){
                $('.body').append(data);
            }
        })
    })
})
</script>''' % post_body


@app.route('/more')
def load_post():
    return generate_lorem_ipsum(n=1)


# redirect to last page
@app.route('/foo')
def foo():
    return '<h1>Foo page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)


@app.route('/bar')
def bar():
    return '<h1>Bar page</h1><a href="%s">Do something and redirect</a>' \
           % url_for('do_something', next=request.full_path)


@app.route('/do-something')
def do_something():
    # do something here
    return redirect_back()


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


def redirect_back(default='hello', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))
