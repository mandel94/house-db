from settings import SETTINGS
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/settings/messaging/<framework>', methods=['GET'])
def get_messaging_settings(framework):
    return jsonify(SETTINGS['messaging'][framework])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)








    

    
