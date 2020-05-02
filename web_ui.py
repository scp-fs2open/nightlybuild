import argparse
import sys
import yaml
from subprocess import Popen, STDOUT
from flask import Flask, request, abort

parser = argparse.ArgumentParser()
parser.add_argument("--config", help="Sets the config file", default="config.yml")

args = parser.parse_args()

config = {}

with open(args.config, "r") as f:
    try:
        config = yaml.load(f)
    except yaml.YAMLError as e:
        print(e)
        sys.exit(1)


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello stranger!'


@app.route('/trigger/release')
def trigger_release():
    if request.args.get('api_key') != config['webui']['key']:
        abort(403)

    args = [request.args['version']]
    if 'tag_name' in request.args and request.args['tag_name'] != '':
        args.append(request.args['tag_name'])

    Popen([sys.executable, 'release.py'] + args, stdout=open('release.log', 'w'), stderr=STDOUT)

    return 'OK'


application = app
