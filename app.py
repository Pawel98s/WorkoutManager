from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:lahata@localhost:5432/workout'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(20), nullable=False)


class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)


class Set(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercise.id'), nullable=False)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    set_number = db.Column(db.Integer)


def seed_exercises():
    exercise_names = [
        "Wyciskanie sztangi leżąc",
        "Wyciskanie hantli leżąc",
        "Wyciskanie sztangi na ławce skośnej",
        "Wyciskanie hantli na ławce skośnej",
        "Rozpiętki z hantlami",
        "Rozpiętki na bramie",
        "Pompki",
        "Pompki na poręczach",
        "Martwy ciąg",
        "Martwy ciąg rumuński",
        "Wiosłowanie sztangą",
        "Wiosłowanie hantlem",
        "Podciąganie nachwytem",
        "Podciąganie podchwytem",
        "Ściąganie drążka do klatki",
        "Przyciąganie linki wyciągu siedząc",
        "Face pull",
        "Szrugsy",
        "Wyciskanie żołnierskie",
        "Wyciskanie hantli siedząc",
        "Arnold press",
        "Unoszenie hantli bokiem",
        "Unoszenie hantli w przód",
        "Odwrotne rozpiętki",
        "Uginanie ramion ze sztangą",
        "Uginanie ramion z hantlami",
        "Uginanie młotkowe",
        "Uginanie na modlitewniku",
        "Wyciskanie francuskie",
        "Prostowanie ramion na wyciągu",
        "Dipy na triceps",
        "Wąskie wyciskanie sztangi",
        "Przysiady ze sztangą",
        "Przysiady przednie",
        "Hack squat",
        "Suwnica",
        "Wykroki z hantlami",
        "Bułgarskie przysiady",
        "Uginanie nóg leżąc",
        "Prostowanie nóg siedząc",
        "Hip thrust",
        "Wspięcia na palce stojąc",
        "Wspięcia na palce siedząc",
        "Glute bridge",
        "Kickback na wyciągu",
        "Przysiad sumo",
        "Brzuszki",
        "Spięcia brzucha",
        "Unoszenie nóg w zwisie",
        "Deska",
        "Russian twist",
        "Allahy na wyciągu",
        "Bieganie na bieżni",
        "Rower stacjonarny",
        "Orbitrek",
        "Skakanka",
        "Burpees"
    ]

    existing_names = {exercise.name for exercise in Exercise.query.all()}
    new_exercises = []

    for name in exercise_names:
        if name not in existing_names:
            new_exercises.append(Exercise(name=name))

    if new_exercises:
        db.session.add_all(new_exercises)
        db.session.commit()


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

        exercise_ids = request.form.getlist('exercise_id[]')
        sets_list = request.form.getlist('sets[]')
        reps_list = request.form.getlist('reps[]')
        weight_list = request.form.getlist('weight[]')

        for i in range(len(exercise_ids)):
            if not exercise_ids[i]:
                continue

            new_set = Set(
                workout_id=workout.id,
                exercise_id=int(exercise_ids[i]),
                reps=int(reps_list[i]) if reps_list[i] else 0,
                weight=float(weight_list[i]) if weight_list[i] else 0,
                set_number=int(sets_list[i]) if sets_list[i] else 0
            )
            db.session.add(new_set)

        db.session.commit()
        return redirect(url_for('mainPage'))

    exercises = Exercise.query.order_by(Exercise.name.asc()).all()
    return render_template('add_workout.html', exercises=exercises)

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
        for s in old_sets:
            db.session.delete(s)

        db.session.commit()

        exercise_ids = request.form.getlist('exercise_id[]')
        sets_list = request.form.getlist('sets[]')
        reps_list = request.form.getlist('reps[]')
        weight_list = request.form.getlist('weight[]')

        for i in range(len(exercise_ids)):
            if not exercise_ids[i]:
                continue

            new_set = Set(
                workout_id=workout.id,
                exercise_id=int(exercise_ids[i]),
                reps=int(reps_list[i]) if reps_list[i] else 0,
                weight=float(weight_list[i]) if weight_list[i] else 0,
                set_number=int(sets_list[i]) if sets_list[i] else 0
            )
            db.session.add(new_set)

        db.session.commit()
        return redirect(url_for('workouts_list'))

    workout_sets = Set.query.filter_by(workout_id=workout.id).all()
    exercises = Exercise.query.order_by(Exercise.name.asc()).all()

    exercises_data = []
    for s in workout_sets:
        exercises_data.append({
            'exercise_id': s.exercise_id,
            'sets': s.set_number,
            'reps': s.reps,
            'weight': s.weight
        })

    return render_template(
        'edit_workout.html',
        workout=workout,
        exercises_data=exercises_data,
        exercises=exercises
    )


@app.route('/history')
def workout_history():
    workouts = Workout.query.order_by(Workout.id.desc()).all()
    history_data = []

    for workout in workouts:
        workout_sets = Set.query.filter_by(workout_id=workout.id).all()
        exercises = []

        for single_set in workout_sets:
            exercise = Exercise.query.get(single_set.exercise_id)
            exercises.append({
                'name': exercise.name if exercise else 'Brak nazwy',
                'set_number': single_set.set_number,
                'reps': single_set.reps,
                'weight': single_set.weight
            })

        history_data.append({
            'id': workout.id,
            'name': workout.name,
            'date': workout.date,
            'exercises': exercises
        })

    return render_template('history.html', history_data=history_data)

@app.route('/analysis', methods=['GET'])
def analysis():
    selected_exercise_id = request.args.get('exercise_id')

    workouts = Workout.query.all()
    sets = Set.query.all()
    exercises = Exercise.query.order_by(Exercise.name.asc()).all()

    total_workouts = len(workouts)

    exercise_counter = {}
    for s in sets:
        exercise_counter[s.exercise_id] = exercise_counter.get(s.exercise_id, 0) + 1

    most_popular_exercise = None
    if exercise_counter:
        most_id = max(exercise_counter, key=exercise_counter.get)
        most_popular_exercise_obj = Exercise.query.get(most_id)
        most_popular_exercise = most_popular_exercise_obj.name if most_popular_exercise_obj else None

    total_sets = 0
    total_volume = 0
    chart_labels = []
    chart_volumes = []

    if selected_exercise_id:
        selected_exercise_id = int(selected_exercise_id)

        filtered_sets = Set.query.filter_by(exercise_id=selected_exercise_id).all()

        total_sets = sum(s.set_number or 0 for s in filtered_sets)
        total_volume = sum((s.weight or 0) * (s.reps or 0) * (s.set_number or 0) for s in filtered_sets)

        for s in filtered_sets:
            workout = Workout.query.get(s.workout_id)
            volume = (s.weight or 0) * (s.reps or 0) * (s.set_number or 0)

            chart_labels.append(workout.date if workout else "Brak daty")
            chart_volumes.append(volume)

    return render_template(
        'analysis.html',
        exercises=exercises,
        total_workouts=total_workouts,
        most_popular_exercise=most_popular_exercise,
        total_sets=total_sets,
        total_volume=round(total_volume, 2),
        chart_labels=chart_labels,
        chart_volumes=chart_volumes,
        selected_exercise_id=selected_exercise_id
    )


with app.app_context():
    db.create_all()
    seed_exercises()

if __name__ == '__main__':
    app.run(debug=True)