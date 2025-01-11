from flask import request, jsonify, render_template, session, flash, redirect, url_for, Blueprint
from app.decorators import login_required
from app.models import User, Message, Channel
from . import db



messages_bp = Blueprint('messages_bp', __name__)


@messages_bp.route('/messages', methods=['GET', 'POST'])
@login_required
def direct():
    username = session.get('user')
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found', "error")
        return redirect(url_for('api.login'))

    selected_chat = None
    return render_template('direct.html', user=user, selected_chat=selected_chat)


@messages_bp.route('/messages/send', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    content = data.get('content')
    receiver_id = data.get('receiver_id')
    channel_id = data.get('channel_id')
    user_id = session.get('user_id')

    if not content:
        return jsonify({'error': 'Message content is required'}), 400

    message = Message(content=content, sender_id=user_id, receiver_id=receiver_id, channel_id=channel_id)
    db.session.add(message)
    db.session.commit()
    return jsonify({'message': 'Message sended succes'}), 201


@messages_bp.route('/messages/create', methods=['POST'])
@login_required
def create_channel():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    user_id = session.get('user_id')

    if not name:
        return jsonify({'error': 'Channel name is required'}), 400

    channel = Channel(name=name, description=description, owner_id=user_id)
    db.session.add(channel)
    db.session.commit()
    return jsonify({'message': 'Channel created successfully!'}), 201


@messages_bp.route('/messages/search', methods=['GET'])
@login_required
def search_channels():
    search_query = request.args.get('search_query')
    channels = Channel.query.filter(Channel.name.ilike(f'%{search_query}%')).all()
    return render_template('channels/channel_search_results.html', channels=channels)