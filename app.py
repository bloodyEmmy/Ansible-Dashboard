import os
from flask import Flask, jsonify, request, render_template
from werkzeug.utils import secure_filename
import database
import generator

app = Flask(__name__)

generator.bootstrap_system()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/history', methods=['GET'])
def api_history():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    user = request.args.get('user')
    playbook = request.args.get('playbook')
    
    try:
        runs = database.get_runs(start_date, end_date, user, playbook)
        return jsonify({"status": "success", "count": len(runs), "data": runs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/playbook/<filename>', methods=['GET'])
def get_playbook(filename):
    safe_name = secure_filename(filename)
    filepath = os.path.join('playbooks', safe_name)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({"status": "success", "content": content}), 200
    else:
        return jsonify({"status": "error", "message": "File not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)