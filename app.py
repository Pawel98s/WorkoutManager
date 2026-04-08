from flask import Flask, request, jsonify, render_template, redirect, url_for
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


@app.route('/add_workout', methods=['GET', 'POST'])
def add_workout():
    if request.method == 'POST':
        workout = Workout(
            name=request.form.get('workout_name'),
            date=request.form.get('workout_date')
        )
        db.session.add(workout)
        db.session.commit()

        exercise_names = request.form.getlist('exercise_name[]')
        sets_list = request.form.getlist('sets[]')
        reps_list = request.form.getlist('reps[]')
        weight_list = request.form.getlist('weight[]')

        for i in range(len(exercise_names)):
            exercise = Exercise(name=exercise_names[i])
            db.session.add(exercise)
            db.session.commit()

            new_set = Set(
                workout_id=workout.id,
                exercise_id=exercise.id,
                reps=int(reps_list[i]),
                weight=float(weight_list[i]) if weight_list[i] else 0,
                set_number=int(sets_list[i])
            )

            db.session.add(new_set)

        db.session.commit()

        return redirect(url_for('mainPage'))

    return render_template('add_workout.html')
@app.route('/workouts')
def workouts_list():
    workouts = Workout.query.order_by(Workout.id.desc()).all()
    return render_template('workouts.html', workouts=workouts)


@app.route('/edit_workout/<int:workout_id>', methods=['GET', 'POST'])
def edit_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)

    if request.method == 'POST':
        workout.name = request.form.get('workout_name')
        workout.date = request.form.get('workout_date')

        old_sets = Set.query.filter_by(workout_id=workout.id).all()
        old_exercise_ids = [s.exercise_id for s in old_sets]

        for s in old_sets:
            db.session.delete(s)

        for exercise_id in old_exercise_ids:
            exercise = Exercise.query.get(exercise_id)
            if exercise:
                db.session.delete(exercise)

        db.session.commit()

        exercise_names = request.form.getlist('exercise_name[]')
        sets_list = request.form.getlist('sets[]')
        reps_list = request.form.getlist('reps[]')
        weight_list = request.form.getlist('weight[]')

        for i in range(len(exercise_names)):
            if not exercise_names[i].strip():
                continue

            exercise = Exercise(name=exercise_names[i])
            db.session.add(exercise)
            db.session.commit()

            new_set = Set(
                workout_id=workout.id,
                exercise_id=exercise.id,
                reps=int(reps_list[i]) if reps_list[i] else 0,
                weight=float(weight_list[i]) if weight_list[i] else 0,
                set_number=int(sets_list[i]) if sets_list[i] else 0
            )
            db.session.add(new_set)

        db.session.commit()
        return redirect(url_for('workouts_list'))

    workout_sets = Set.query.filter_by(workout_id=workout.id).all()
    exercises_data = []

    for s in workout_sets:
        exercise = Exercise.query.get(s.exercise_id)
        exercises_data.append({
            'exercise_name': exercise.name if exercise else '',
            'sets': s.set_number,
            'reps': s.reps,
            'weight': s.weight
        })

    return render_template(
        'edit_workout.html',
        workout=workout,
        exercises_data=exercises_data
    )

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)