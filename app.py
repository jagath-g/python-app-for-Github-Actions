from flask import Flask, jsonify
from werkzeug.routing import BaseConverter

class SignedIntConverter(BaseConverter):
    regex = r'-?\d+'

    def to_python(self, value):
        return int(value)

    def to_url(self, value):
        return str(value)

app = Flask(__name__)
app.url_map.converters['sint'] = SignedIntConverter

@app.route('/')
def hello_world():
    return jsonify(message="Hello from Python Flask App!")

@app.route('/add/<sint:num1>/<sint:num2>')
def add_numbers(num1, num2):
    result = num1 + num2
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
