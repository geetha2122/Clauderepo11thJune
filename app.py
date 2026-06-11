from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
db = SQLAlchemy(app)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'event', 'task', 'reminder'
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    description = db.Column(db.Text)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    date_str = request.args.get('date', datetime.today().strftime('%Y-%m-%d'))
    sessions = Session.query.filter_by(date=datetime.strptime(date_str, '%Y-%m-%d').date()).all()
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'type': s.type,
        'start_time': s.start_time.isoformat() if s.start_time else None,
        'end_time': s.end_time.isoformat() if s.end_time else None,
        'description': s.description
    } for s in sessions])

@app.route('/api/sessions', methods=['POST'])
def create_session():
    data = request.json
    session = Session(
        date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
        title=data['title'],
        type=data['type'],
        start_time=datetime.strptime(data.get('start_time'), '%H:%M').time() if data.get('start_time') else None,
        end_time=datetime.strptime(data.get('end_time'), '%H:%M').time() if data.get('end_time') else None,
        description=data.get('description')
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({'id': session.id}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
