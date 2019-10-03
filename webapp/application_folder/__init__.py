from flask import Flask

app = Flask(__name__)

from application_folder import routes
