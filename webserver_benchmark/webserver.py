from flask import Flask, jsonify, request

# Create the Flask app
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "<h1>Welcome to the Flask Web Server!</h1>"

# API route that returns JSON
@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'name': 'Flask Example',
        'message': 'This is a simple Flask web server!',
        'status': 'success'
    }
    return jsonify(data)

# Example route with query parameters
@app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'Guest')  # Default value is 'Guest' if no name is provided
    return jsonify({"message": f"Hello, {name}!"})

# POST example that accepts JSON data
@app.route('/api/echo', methods=['POST'])
def echo():
    if request.is_json:
        data = request.get_json()
        return jsonify({"you_sent": data}), 200
    else:
        return jsonify({"error": "Invalid input, expecting JSON"}), 400

# Start the Flask web server
if __name__ == '__main__':
    app.run(debug=True)
