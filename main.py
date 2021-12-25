from flask import Flask, request, jsonify
from werkzeug.wrappers import Request, Response
from werkzeug.utils import secure_filename

home_team_global = ''
away_team_global = ''

app = Flask(__name__)

@app.route('/api/v1.0/teamlogo', methods = ['POST'])
def addTeamLogo():
    file = request.files['file']
    # Read the image via file.stream
    file.save('teamLogos/' + secure_filename(file.filename))

    return jsonify({'msg': 'success'})

@app.route('/api/v1.0/teamandplayers', methods = ['POST'])
def teamandplayers():
    home_team_global = request.get_json()
    away_team_global = request.get_json()
    
    return jsonify({'msg': 'success'})

if __name__ == '__main__':
    app.run(debug=True)