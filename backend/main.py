from flask import Flask, send_from_directory
import os
from flask_cors import CORS
from pprint import pprint
from routes.routes import api_bp # oder in __init__.py importieren

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, '../spoty-star/dist/assets'),
    template_folder=os.path.join(BASE_DIR, '../spoty-star/dist')
)
app.secret_key = os.getenv('SECRET_KEY') # für Flask-Session
app.register_blueprint(api_bp)

cors = CORS(app, origins="*") #TODO change later



@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

if __name__ == '__main__':
    # python3 app.py
    app.run(host="localhost", port=5001, debug=True)
