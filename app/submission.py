import subprocess
from flask import request, jsonify, render_template
from .models import Submission, Problem, User, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app as app
import json

# @app.route('/submit', methods=['POST'])
# @jwt_required()
# def submit_code():
#     data = request.get_json()
#     user = User.query.filter_by(username=get_jwt_identity()).first()

#     problem = Problem.query.get_or_404(data.get('problem_id'))
#     code = data.get('code')

#     submission = Submission(user_id=user.id, problem_id=problem.id, code=code, status='Pending')
#     db.session.add(submission)
#     db.session.commit()

#     result, status = evaluate_code(problem, code) # To be replaced with sandbox env 

#     submission.status = status
#     submission.result = result
#     db.session.commit()

#     return jsonify({"message": "Submission evaluated", "status": status, "result": result}), 200

# @app.route('/submissions', methods=['GET'])
# @jwt_required()
# def get_submission_history():
#     user = User.query.filter_by(username=get_jwt_identity()).first()

#     submissions = Submission.query.filter_by(user_id=user.id).all()
#     submission_history = []

#     for submission in submissions:
#         problem = Problem.query.get(submission.problem_id)
#         submission_data = {
#             'problem_title': problem.title,
#             'status': submission.status,
#             'result': submission.result,
#             'timestamp': submission.timestamp.strftime('%Y-%m-%d %H:%M:%S')
#         }
#         submission_history.append(submission_data)

#     return jsonify(submission_history), 200

# Using exec command in python
# def evaluate_code(problem, code):
#     try:
#         # print("inside try")
#         exec_globals = {}
#         exec(code, exec_globals)
#         user_func = None

#         for key, value in exec_globals.items():
#             if callable(value):
#                 user_func = value
#                 break
#         # print(user_func)
#         if user_func is None:
#             return "No callable function found", "Failed"
        
#         # print(problem.sample_input, problem.sample_output)
#         expected_output = eval(problem.sample_output)
#         actual_output = user_func(*eval(problem.sample_input))
#         # print(problem.sample_input, problem.sample_output)
#         if actual_output == expected_output:
#             return "Correct", "Success"

#         else:
#             return "Output does not match", "Failed"

#     except Exception as e:
#         return str(e), "Error"

# Using Docker image for evaluating code
def evaluate_code(problem, code):
    try:
        exec_globals = {}
        exec(code, exec_globals)
        user_func = None

        for key, value in exec_globals.items():
            if callable(value):
                user_func = value
                break
        
        if user_func is None:
            return "No callable function found", "Failed", ""
        
        input_str = problem.sample_input
        input_dict = eval(f"dict({input_str})")
        serialized_input = json.dumps(input_dict)
        
        print("Running Docker")
        command = [
            "docker", "run", "--rm",
            "--network", "none", 
            "codingplatform:latest", user_func.__name__, code, serialized_input
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print("Printing Result", result)

        if result.returncode != 0:
            return result.stderr.strip(), "Error", ""

        # Split the output into lines
        output_lines = result.stdout.strip().split('\n')
        
        # The last line should be our JSON result
        try:
            output = json.loads(output_lines[-1])
            print("Printing Output", output)
            print("Printing Output Status", output['status'])
            print("Printing Output Result", output['result'])
            
            # Join all lines except the last one as user's print output
            user_print_output = '\n'.join(output_lines[:-1])
            print("User's print output:", user_print_output)

            if output['status'] == "Success" and output['result'] == eval(problem.sample_output):
                return "Correct", "Success", user_print_output
            else:
                return output['result'], "Failed", user_print_output
        except json.JSONDecodeError:
            return f"Invalid output format", "Error", result.stdout

    except Exception as e:
        return str(e), "Error", ""

@app.route('/problems/<int:problem_id>/solve', methods=['POST'])
@jwt_required()
def solve_problem(problem_id):
    data = request.get_json()
    user = User.query.filter_by(username=get_jwt_identity()).first()

    problem = Problem.query.get_or_404(problem_id)
    code = data.get('code')

    submission = Submission(user_id=user.id, problem_id=problem.id, code=code, status='Pending')
    db.session.add(submission)
    db.session.commit()

    result, status, user_print = evaluate_code(problem, code)

    submission.status = status
    submission.result = result
    db.session.commit()

    return jsonify({
        "message": "Submission evaluated", 
        "status": status, 
        "result": result, 
        "user_print": user_print
    }), 200

@app.route('/problems/<int:problem_id>/solve', methods=['GET'])
@jwt_required()
def problem_solve(problem_id):
    problem = Problem.query.get_or_404(problem_id)
    return render_template('problem_solve.html', problem=problem)

@app.route('/problems/<int:problem_id>/submissions')
@jwt_required()
def problem_submissions(problem_id):
    user = User.query.filter_by(username=get_jwt_identity()).first()
    problem = Problem.query.get_or_404(problem_id)

    submissions = Submission.query.filter_by(user_id=user.id, problem_id=problem.id).order_by(Submission.timestamp.desc()).all()
    submission_history = []

    for submission in submissions:
        problem = Problem.query.get(submission.problem_id)
        submission_data = {
            'problem_title': problem.title,
            'status': submission.status,
            'result': submission.result,
            'timestamp': submission.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'code': submission.code
        }
        submission_history.append(submission_data)

    return jsonify(submission_history), 200
