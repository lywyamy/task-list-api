from flask import Blueprint, jsonify, request, abort, make_response
from app import db
from app.models.task import Task
from app.models.goal import Goal
from datetime import datetime


tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goals_bp = Blueprint("goals", __name__, url_prefix="/goals")

#***********************************************#
#***************** Task Routes *****************#
#***********************************************#

@tasks_bp.route("", methods=["POST"])
def add_one_task():
    return create_one_model(Task, request.get_json())


@tasks_bp.route("", methods=["GET"])
def get_all_tasks():
    return get_all_models(Task, request.args.get("sort"))


@tasks_bp.route("/<task_id>", methods=["GET"])
def get_one_task(task_id):
    return get_one_model(Task, task_id)


@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_one_task(task_id):
    return update_one_model(Task, task_id, request.get_json())


@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_one_task(task_id):
    return delete_one_model(Task, task_id)


@tasks_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def mark_one_task_as_complete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = datetime.now()

    db.session.commit()

    return jsonify(generate_response_body(Task, task)), 200


@tasks_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def mark_one_task_as_incomplete(task_id):
    task = validate_model(Task, task_id)

    task.completed_at = None

    db.session.commit()

    return jsonify(generate_response_body(Task, task)), 200

#***********************************************#
#***************** Goal Routes *****************#
#***********************************************#

@goals_bp.route("", methods=["POST"])
def add_one_goal():
    return create_one_model(Goal, request.get_json())


@goals_bp.route("", methods=["GET"])
def get_all_goals():
    return get_all_models(Goal)


@goals_bp.route("/<goal_id>", methods=["GET"])
def get_one_goal(goal_id):
    return get_one_model(Goal, goal_id)


@goals_bp.route("/<goal_id>", methods=["PUT"])
def update_one_goal(goal_id):
    return update_one_model(Goal, goal_id, request.get_json())


@goals_bp.route("/<goal_id>", methods=["DELETE"])
def delete_one_goal(goal_id):
    return delete_one_model(Goal, goal_id)

#************************************************#
#*************** Helper Functions ***************#
#************************************************#

def generate_response_body(cls, models):
    """
    Return a list of model-detail dictionaries if @param models is a list of Model objects
    Return a single dictionary {"model": model-detail} if @param models is a Model object
    """
    if isinstance(models, list):
        response = []

        for model in models:
            response.append(cls.to_dict(model))

        return response
    
    else:
        return {
            f"{cls.__name__}".lower(): cls.to_dict(models)
        }


def validate_model(cls, model_id):
    try:
        model_id = int(model_id)
    except:
        response_body = {
            "message": f"{cls.__name__} id {model_id} is invalid."
        }

        abort(make_response(jsonify(response_body), 400))
    
    model = cls.query.get(model_id)

    if model is None:
        response_body = {
            "message": f"{cls.__name__} {model_id} is does not exist."
        }

        abort(make_response(jsonify(response_body), 404))

    return model


def get_one_model(cls, model_id):
    model = validate_model(cls, model_id)

    return jsonify(generate_response_body(cls, model)), 200


def delete_one_model(cls, model_id):
    model = validate_model(cls, model_id)

    db.session.delete(model)
    db.session.commit()

    response_body = {
        "details": f"{cls.__name__} {model.id} \"{model.title}\" successfully deleted"
    }

    return jsonify(response_body), 200


def create_one_model(cls, request_dict):
    try:
        model = cls.create_from_dict(request_dict)

        db.session.add(model)
        db.session.commit()

    except:
        response_body = {
            "details": "Invalid data"
        }

        abort(make_response(jsonify(response_body), 400))
    
    return jsonify(generate_response_body(cls, model)), 201


def update_one_model(cls, model_id, request_dict):
    model = validate_model(cls, model_id)

    try:
        cls.update_from_dict(model, request_dict)

        db.session.commit()
    
    except:
        response_body = {
            "details": "Invalid data"
        }

        abort(make_response(jsonify(response_body), 400))

    return jsonify(generate_response_body(cls, model)), 200


def get_all_models(cls, order=None):
    if order == "asc":
        models = cls.query.order_by(cls.title).all()
    elif order == "desc":
        models = cls.query.order_by(cls.title.desc()).all()
    else:
        models = cls.query.all()
    
    return jsonify(generate_response_body(cls, models)), 200