from flask import current_app as app, jsonify, render_template

@app.route('/')
def index():
    return render_template('index.html')

