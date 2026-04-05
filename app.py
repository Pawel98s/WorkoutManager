from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lahata@localhost:5432/workout'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)



class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    date = db.Column(db.String(20))

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

class Set(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'))
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'))
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    set_number = db.Column(db.Integer)



@app.route('/')
def mainPage():
    return render_template('index.html')

@app.route('/add-workout', methods=['POST'])
def add_workout():
    data = request.json

    workout = Workout(
        name=data.get('name'),
        date=data.get('date')
    )

    db.session.add(workout)
    db.session.commit()

    return jsonify({"message": "Workout added"})


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)