from flask import request, jsonify, render_template, redirect, url_for
from .models import Problem, db
from flask_jwt_extended import jwt_required
from flask import current_app as app


@app.route('/problems/add', methods=['GET', 'POST'])
@jwt_required()
def add_problem():
    if request.method == 'POST':
        data = request.get_json()
        new_problem = Problem(
            title=data.get('title'),
            description=data.get('description'),
            difficulty=data.get('difficulty'),
            input_format=data.get('input_format'),
            output_format=data.get('output_format'),
            sample_input=data.get('sample_input'),
            sample_output=data.get('sample_output'),
            sample_code=data.get('sample_code'),
            constraints=data.get('constraints')
        )
        db.session.add(new_problem)
        db.session.commit()
        return jsonify({"message": "Problem added successfully", "problem": data}), 201

    return render_template('add_problem.html')

@app.route('/problems', methods=['GET'])
def list_problems():
    problems = get_all_problems()
    return render_template('problems.html', problems=problems)

@app.route('/problems/<int:problem_id>', methods=['GET'])
def problem_details(problem_id):
    problem = get_problem_by_id(problem_id)
    if problem is None:
        return "Problem not found", 404
    return render_template('problem_details.html', problem=problem)

@app.route('/problems/<int:id>', methods=['PUT'])
@jwt_required()
def update_problem(id):
    problem = Problem.query.get_or_404(id)
    data = request.get_json()
    
    problem.title = data.get('title', problem.title)
    problem.description = data.get('description', problem.description)
    problem.difficulty = data.get('difficulty', problem.difficulty)
    problem.input_format = data.get('input_format', problem.input_format)
    problem.output_format = data.get('output_format', problem.output_format)
    problem.sample_input = data.get('sample_input', problem.sample_input)
    problem.sample_output = data.get('sample_output', problem.sample_output)
    problem.sample_code = data.get('sample_code', problem.sample_code)
    problem.constraints = data.get('constraints', problem.constraints)

    db.session.commit()
    return jsonify({"message": "Problem updated successfully"}), 200

@app.route('/problems/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_problem(id):
    problem = Problem.query.get_or_404(id)
    db.session.delete(problem)
    db.session.commit()
    return jsonify({"message": "Problem deleted successfully"}), 200

def get_all_problems():
    return Problem.query.all()

def get_problem_by_id(problem_id):
    return Problem.query.get(problem_id)
