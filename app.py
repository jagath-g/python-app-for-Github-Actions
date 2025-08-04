from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return jsonify(message="Hello from Python Flask App!")

@app.route('/add/<int:num1>/<int:num2>')
def add_numbers(num1, num2):
    result = num1 + num2
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
