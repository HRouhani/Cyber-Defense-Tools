"""Fictional server-only service: not published to the Kali host."""
from flask import Flask, jsonify
app = Flask(__name__)

@app.get('/metadata')
def metadata():
    return jsonify({
        'instance_id': 'i-training-demo-0001',
        'model': 'llama3.2:1b',
        'environment': 'isolated-training-network',
        'training_only': True,
        'note': 'Fictional metadata: no cloud credentials or live tokens.'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8765, debug=False)
