from flask import Flask, jsonify, request
from absl import app as absl_app, flags

FLAGS = flags.FLAGS
flags.DEFINE_integer('port', 8000, 'Port number to run the Flask app.')

# Create the Flask app
flask_app = Flask(__name__)

def preprocess(query):
    """[SUT Node] A dummy preprocess."""
    response = query
    return response

def dnn_model(query):
    """[SUT Node] A dummy DNN model."""
    response = "The output of DNN model:" + query  
    return response

def postprocess(query):
    """[SUT Node] A dummy postprocess."""
    response = query
    return response

# Home route
@flask_app.route('/')
def home():
    return "<h1>Welcome to the Flask Web Server!</h1>"

@flask_app.route('/predict/', methods=['POST'])
def predict():
    query = request.get_json(force=True)['query']
    bkendquery = preprocess(query)
    bkendresult = dnn_model(bkendquery)
    result = postprocess(bkendresult)
    return jsonify(result=result)

@flask_app.route('/getname/', methods=['POST', 'GET'])
def getname():
    return jsonify(name="Web Server SUT node")

# API route that returns JSON
@flask_app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'name': 'Flask Example',
        'message': 'This is a simple Flask web server!',
        'status': 'success'
    }
    return jsonify(data)

# Example route with query parameters
@flask_app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'Guest')  # Default value is 'Guest' if no name is provided
    return jsonify({"message": f"Hello, {name}!"})

# POST example that accepts JSON data
@flask_app.route('/api/echo', methods=['POST'])
def echo():
    if request.is_json:
        data = request.get_json()
        return jsonify({"you_sent": data}), 200
    else:
        return jsonify({"error": "Invalid input, expecting JSON"}), 400

def main(argv):
    # This starts the Flask app
    flask_app.run(debug=True, port=FLAGS.port)

# Start the Flask web server using absl.app
if __name__ == '__main__':
    absl_app.run(main)
