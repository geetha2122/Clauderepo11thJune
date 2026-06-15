from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendar.db'
db = SQLAlchemy(app)

DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M'


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    description = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'type': self.type,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'description': self.description
        }

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, DATE_FORMAT).date()
    except ValueError:
        return None


def parse_time(time_str):
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, TIME_FORMAT).time()
    except ValueError:
        return None


@app.route('/')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    date_str = request.args.get('date', datetime.today().strftime(DATE_FORMAT))
    date_obj = parse_date(date_str)
    if date_obj is None:
        return jsonify({'error': 'Invalid date format'}), 400
    sessions = Session.query.filter_by(date=date_obj).all()
    return jsonify([s.to_dict() for s in sessions])

@app.route('/api/sessions', methods=['POST'])
def create_session():
    data = request.json
    date_obj = parse_date(data.get('date', ''))
    if date_obj is None:
        return jsonify({'error': 'Invalid date format'}), 400

    start_time = parse_time(data.get('start_time'))
    end_time = parse_time(data.get('end_time'))

    session = Session(
        date=date_obj,
        title=data['title'],
        type=data['type'],
        start_time=start_time,
        end_time=end_time,
        description=data.get('description')
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({'id': session.id}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
