from flask import Flask, render_template, request, redirect, make_response
from . import db, app
from .model import User, Funds
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
from sqlalchemy.sql import func

@app.route("/signup", methods=["POST"])
def signup():
    user = User()
    user.firstname = request.form["firstname"]
    user.lastname = request.form["lastname"]
    user.email = request.form["email"]
    user.password = generate_password_hash(request.form["password"])
    if user.firstname == "" or user.lastname == "" or user.email == "" or user.password == "":
        return make_response({
            "message": "All fields are required",
            "status": 400
        })
    elif db.session.query(User).filter(User.email == user.email).count() > 0:
        return make_response({
            "message": "Email already exists",
            "status": 400
        })
    else:
        db.session.add(user)
        db.session.commit()
        return make_response({
            "message": "User created",
            "status": 201
        })
    
    return make_response({
        "message": "An error occurred",
        "status": 500
    })


@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    user = db.session.query(User).filter(User.email == email).first()

    if user is None:
        return make_response({
            "message": "User does not exist",
            "status": 404
        })
    elif not check_password_hash(user.password, password):
        return make_response({
            "message": "Invalid password",
            "status": 400
        })
    else:
        token = jwt.encode(
            {"id": user.id,
             "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
            }, 
            "secret_key", 
            algorithm="HS256"
        )
        return make_response({
            'token': token,
        })
    
    return make_response({
        "message": "An error occurred",
        "status": 500
    })

def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        token=None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return make_response({
                "message": "Token is missing",
                "status": 401
            })
        
        try:
            data = jwt.decode(token, "secret_key", algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
            print(current_user)
        except:
            return make_response({
                "message": "Token is invalid",
                "status": 401
            })
        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/funds", methods=["GET"])
@token_required
def getAllfunds(current_user):
    funds = Funds.query.filter_by(user_id=current_user.id).all()
    totalSum = 0
    if funds:
        totalSum = Funds.query.with_entities(db.func.round(func.sum(Funds.amount), 2)).filter_by(user_id=current_user.id).all()[0][0]
        print(totalSum)
    return make_response({
        "data": [row.serialize for row in funds],
        "sum": totalSum
    })

@app.route("/funds", methods=["POST"])
@token_required
def createFund(current_user):
    fund = Funds()
    fund.user_id = current_user.id
    fund.amount = request.form["amount"]
    if fund.amount == "":
        return make_response({
            "message": "Amount is required",
            "status": 400
        })
    
    if fund.amount:
        db.session.add(fund)
        db.session.commit()
    return fund.serialize

@app.route("/funds/<int:id>", methods=["PUT"])
@token_required
def managefund(current_user, id):
    try:
        fund = Funds.query.filter_by(user_id=current_user.id, id=id).first() 
        if fund:
            fund.amount = request.form["amount"]
            db.session.commit()
            return make_response({
                "message": "Fund updated",
                "status": 200
            })
        return make_response({
            "message": "Fund not found",
            "status": 404
        })
    except Exception as e:
        return make_response({
            "message": "An error occurred",
            "status": 500
        })

@app.route("/funds/<int:id>", methods=["DELETE"])
@token_required
def deletefund(current_user, id):
    try:
        fund = Funds.query.filter_by(user_id=current_user.id, id=id).first() 
        if fund:
            db.session.delete(fund)
            db.session.commit()
            return make_response({
                "message": "Fund deleted",
                "status": 200
            })
        return make_response({
            "message": "Fund not found",
            "status": 404
        })
    except Exception as e:
        return make_response({
            "message": "An error occurred",
            "status": 500
        })