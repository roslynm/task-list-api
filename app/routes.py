import datetime
from typing import ChainMap
from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import request, Blueprint, make_response, jsonify
from datetime import datetime
from dotenv import load_dotenv
import os
import requests


load_dotenv()


task_bp = Blueprint("task_bp", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goal_bp", __name__, url_prefix="/goals")


@task_bp.route("", methods=["GET", "POST"])
def handle_tasks():
    task_response = []
    if request.method == "GET":
        if request.args.get("sort") == "asc":
            tasks = Task.query.order_by(Task.title.asc())
        elif request.args.get("sort") == "desc":
            tasks = Task.query.order_by(Task.title.desc())
        else:
            tasks = Task.query.all()
        task_response = [task.to_dict() for task in tasks]
        return jsonify(task_response), 200
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return make_response({"details": "Invalid data"}, 400) 
        new_task = Task(title=request_body["title"],
                        description=request_body["description"], 
                        completed_at=request_body["completed_at"])
        db.session.add(new_task)
        db.session.commit()
        return make_response({"task": new_task.to_dict()}, 201)


@task_bp.route("/<task_id>", methods=["GET", "DELETE", "PUT"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if request.method == "GET":
        if not task:
            return make_response(f"Book {task_id} not found", 404)
        return {"task": task.to_dict()}
    elif request.method == "DELETE":
        if not task:
            return make_response("", 404)
        db.session.delete(task)
        db.session.commit()
        return {"details": f'Task {task.task_id} "{task.title}" successfully deleted'}
    elif request.method == "PUT":
        if not task:
            return make_response("", 404)
        request_body = request.get_json()
        task.title = request_body["title"] if "title" in request_body else task.title
        task.description = request_body["description"] if "description" in request_body else task.description
        task.completed_at = request_body["completed_at"] if "completed_at" in request_body else task.completed_at
        db.session.commit()
        return make_response({"task": task.to_dict()}, 200)


@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])
def handle_task_complete(task_id):
        task = Task.query.get(task_id)
        if not task:
            return make_response(f"Book {task_id} not found", 404)
        task.completed_at = datetime.utcnow()
        db.session.commit()
        initiate_slack_message(task)
        return make_response({"task": task.to_dict()}, 200)


@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])
def handle_task_incomplete(task_id):
        task = Task.query.get(task_id)
        if not task:
            return make_response(f"Book {task_id} not found", 404)
        task.completed_at = None
        db.session.commit()
        return make_response({"task": task.to_dict()}, 200)


@goal_bp.route("", methods=["GET", "POST"])
def handle_goals():
    goal_response = []
    if request.method == "GET":
        goals = Goal.query.all()
        goal_response = [goal.to_dict() for goal in goals]
        return jsonify(goal_response), 200
    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            return make_response({"details": "Invalid data"}, 400) 
        new_goal = Goal(title=request_body["title"])
        db.session.add(new_goal)
        db.session.commit()
        return make_response({"goal": new_goal.to_dict()}, 201)


@goal_bp.route("/<goal_id>", methods=["GET", "DELETE", "PUT"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if request.method == "GET":
        if not goal:
            return make_response(f"Goal {goal_id} not found", 404)
        return {"goal": goal.to_dict()}
    elif request.method == "DELETE":
        if not goal:
            return make_response("", 404)
        db.session.delete(goal)
        db.session.commit()
        return {"details": f'Goal {goal.id} "{goal.title}" successfully deleted'}
    elif request.method == "PUT":
        if not goal:
            return make_response("", 404)
        request_body = request.get_json()
        goal.title = request_body["title"] if "title" in request_body else goal.title
        db.session.commit()
        return make_response({"goal": goal.to_dict()}, 200)


@goal_bp.route("/<goal_id>/tasks", methods=["GET", "POST"])
def handle_goal_tasks(goal_id):
    goal = Goal.query.get(goal_id)
    if goal is None:
        return make_response("", 404)
    if request.method == "POST":
        request_body = request.get_json()
        goal_tasks = request_body["task_ids"]
        for task_id in goal_tasks:
            task = Task.query.get(task_id)
            task.goal_id = goal_id 
        db.session.commit()
        return make_response({"id": int(goal_id), "task_ids": goal_tasks}, 200)
    elif request.method == "GET":
        return goal.dict_with_tasks(), 200


def initiate_slack_message(task):
    SLACKBOT_KEY = os.environ.get("SLACK_BOT")
    CHANNEL = os.environ.get("CHANNEL")
    url = "https://slack.com/api/chat.postMessage"
    message = f"Someone just completed the task {task.title}"
    query_params = {"token":SLACKBOT_KEY, "channel": CHANNEL, "text": message}
    requests.post(url, data=query_params)



