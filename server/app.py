from flask import Flask, request, jsonify
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

@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.all()
    return jsonify([message.to_dict() for message in messages]), 200

@app.route('/messages/<int:id>', methods=['GET'])
def get_message_by_id(id):
    message = db.session.get(Message, id)
    if message:
        return jsonify(message.to_dict()), 200
    return jsonify({"error": "Message not found"}), 404

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data or "body" not in data or "username" not in data:
        return jsonify({"error": "Invalid input"}), 400

    new_message = Message(body=data["body"], username=data["username"])
    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)
    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()
    if "body" in data:
        message.body = data["body"]
    
    db.session.commit()
    return jsonify(message.to_dict()), 200

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)
    if message:
        db.session.delete(message)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200
    return jsonify({"error": "Message not found"}), 404

@app.before_first_request
def seed_database():
    if not Message.query.first():
        message1 = Message(body="Hello World", username="Alice")
        message2 = Message(body="How are you?", username="Bob")
        db.session.add_all([message1, message2])
        db.session.commit()

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Chatterbox API!"})


if __name__ == '__main__':
    seed_database()
    app.run(port=5555)

