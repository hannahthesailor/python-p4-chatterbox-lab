from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages')
def messages():
    messages = Message.query.all()

    # Serialize messages to JSON
    serialized_messages = [{
        'id': message.id,
        'body': message.body,
        'username': message.username,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime as string
    } for message in messages]

    # Return JSON response
    return jsonify(serialized_messages)

@app.route('/messages/<int:id>')
def messages_by_id(id):
    return ''

@app.route('/messages', methods=['POST'])
def create_message():
    # Extract data from the request JSON
    data = request.json
    body = data.get('body')
    username = data.get('username')

    # Validate data
    if not body or not username:
        return jsonify({'error': 'Body and username are required'}), 400

    # Create a new message object
    new_message = Message(body=body, username=username)

    # Add the new message to the database
    db.session.add(new_message)
    db.session.commit()

    # Return the created message as JSON response
    return jsonify({
        'id': new_message.id,
        'body': new_message.body,
        'username': new_message.username,
        'created_at': new_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 201


@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    # Retrieve the session from the database
    session = db.session

    # Retrieve the message from the database by its ID
    message = session.get(Message, id)

    # Check if the message exists
    if message is None:
        return jsonify({'error': 'Message not found'}), 404

    # Extract the updated body from the request JSON
    updated_body = request.json.get('body')

    # Check if the updated body is provided
    if updated_body is None:
        return jsonify({'error': 'Body is required for updating message'}), 400

    # Update the body of the message
    message.body = updated_body

    # Commit the changes to the database
    session.commit()

    # Return the updated message as a JSON response
    return jsonify({
        'id': message.id,
        'body': message.body,
        'username': message.username,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    # Retrieve the session from the database
    session = db.session

    # Retrieve the message from the database by its ID
    message = session.get(Message, id)

    # Check if the message exists
    if message is None:
        return jsonify({'error': 'Message not found'}), 404

    # Delete the message from the database
    session.delete(message)
    session.commit()

    return jsonify({'message': 'Message deleted successfully'}), 200



if __name__ == '__main__':
    app.run(port=5555)
