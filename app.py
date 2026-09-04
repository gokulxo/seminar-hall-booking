from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking.db'
app.config['SECRET_KEY'] = 'change-this-secret-key'
db = SQLAlchemy(app)


# ---------- Models ----------
class Hall(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    slots = db.relationship('Slot', backref='hall', lazy=True)


class Slot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hall_id = db.Column(db.Integer, db.ForeignKey('hall.id'), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time_range = db.Column(db.String(50), nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    booking = db.relationship('Booking', backref='slot', uselist=False)


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    booked_by = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ---------- Routes ----------
@app.route('/')
def index():
    halls = Hall.query.all()
    return render_template('index.html', halls=halls)


@app.route('/hall/<int:hall_id>')
def hall_detail(hall_id):
    hall = Hall.query.get_or_404(hall_id)
    slots = Slot.query.filter_by(hall_id=hall_id).all()
    return render_template('hall_detail.html', hall=hall, slots=slots)


@app.route('/book/<int:slot_id>', methods=['GET', 'POST'])
def book_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)

    if slot.is_booked:
        flash('This slot is already booked!', 'danger')
        return redirect(url_for('hall_detail', hall_id=slot.hall_id))

    if request.method == 'POST':
        name = request.form.get('name')
        purpose = request.form.get('purpose')

        new_booking = Booking(slot_id=slot.id, booked_by=name, purpose=purpose)
        slot.is_booked = True
        db.session.add(new_booking)
        db.session.commit()

        flash('Slot booked successfully!', 'success')
        return redirect(url_for('hall_detail', hall_id=slot.hall_id))

    return render_template('book_slot.html', slot=slot)


# ---------- Seed sample data ----------
def seed_data():
    if Hall.query.count() == 0:
        hall1 = Hall(name='Main Seminar Hall', capacity=200)
        hall2 = Hall(name='Mini Conference Room', capacity=50)
        db.session.add_all([hall1, hall2])
        db.session.commit()

        slots = [
            Slot(hall_id=hall1.id, date='2026-09-10', time_range='9:00 AM - 11:00 AM'),
            Slot(hall_id=hall1.id, date='2026-09-10', time_range='11:00 AM - 1:00 PM'),
            Slot(hall_id=hall1.id, date='2026-09-11', time_range='2:00 PM - 4:00 PM'),
            Slot(hall_id=hall2.id, date='2026-09-10', time_range='10:00 AM - 12:00 PM'),
            Slot(hall_id=hall2.id, date='2026-09-12', time_range='3:00 PM - 5:00 PM'),
        ]
        db.session.add_all(slots)
        db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(host='127.0.0.1', port=5001, debug=True)