from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
import json
import os.path
from werkzeug.utils import secure_filename

bp = Blueprint('urlshort', __name__)

@bp.route('/')
def home():
    return render_template("index.html", codes = session.keys())

@bp.route('/your-url', methods = ['GET','POST'])
def your_url():
    if request.method == "POST":
        urls = {}

        if os.path.exists('urls.json'):
            with open('urls.json') as urls_file:
                urls = json.load(urls_file)
        
        if request.form['code'] in urls.keys():
            flash('Short name is already taken. Please select new one.')
            return redirect(url_for('urlshort.home'))

        #to check if user is trying to shorten 'url' or a 'file'.
        if 'url' in request.form.keys():
            urls[request.form['code']] = {'url':request.form['url']}
        else:
            f = request.files['file']
            #secure_filename makes sure that no malicious file is uploaded.
            full_name = request.form['code'] + secure_filename(f.filename)
            f.save('/home/prajwal/Desktop/flask_practice/url_shortner/urlshort/static/user_files/'+full_name)

            urls[request.form['code']] = {'file':full_name}

        with open('urls.json', 'w') as url_file:
            json.dump(urls, url_file)
            #saving in cookie
            session[request.form['code']] = True

        #when working with POST request to get parameter information we use .form instead of .args...
        return render_template("your_url.html", code = request.form['code'])
    else:
        flash("Try new URL")
        return redirect(url_for("urlshort.home"))

@bp.route('/<string:code>')
def redirect_to_url(code):
    if os.path.exists('urls.json'):
        with open('urls.json') as urls_file:
            urls = json.load(urls_file)
    
            if code in urls.keys():
                if 'url' in urls[code].keys():
                    return redirect(urls[code]['url'])
                else:
                    return redirect(url_for('static', filename = 'user_files/' + urls[code]['file']))

    return abort(404)

@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404