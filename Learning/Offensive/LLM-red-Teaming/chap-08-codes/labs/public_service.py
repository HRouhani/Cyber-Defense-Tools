"""Allowlisted example HTTP destination for safe fetch tests."""
from flask import Flask, jsonify
app = Flask(__name__)

@app.get('/hello')
def hello():
    return jsonify({'message': 'Public lab content', 'training_only': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8766, debug=False)
