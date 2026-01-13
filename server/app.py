from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import datetime

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
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([message.to_dict() for message in messages])

@app.route('/messages/<int:id>')
def messages_by_id(id):
    message = Message.query.get(id)
    if message:
        return jsonify(message.to_dict())
    else:
        return jsonify({'error': 'Message not found'}), 404

@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    body = data.get('body')
    username = data.get('username')
    if body and username:
        message = Message(body=body, username=username)
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict()), 201
    else:
        return jsonify({'error': 'Body and username are required'}), 400

@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = Message.query.get(id)
    if message:
        data = request.get_json()
        body = data.get('body')
        if body:
            message.body = body
            message.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify(message.to_dict())
        else:
            return jsonify({'error': 'Body is required'}), 400
    else:
        return jsonify({'error': 'Message not found'}), 404

@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = Message.query.get(id)
    if message:
        db.session.delete(message)
        db.session.commit()
        return jsonify({'message': 'Message deleted'})
    else:
        return jsonify({'error': 'Message not found'}), 404

if __name__ == '__main__':
    app.run(port=5555)
