from .memberSchemas import member_schema, members_schema
from flask import request, jsonify 
from marshmallow import ValidationError
from sqlalchemy import select
from application.models import Member, db
from . import members_bp
from application.extensions import limiter, cache
from application.utils.util import encode_token, token_required



@members_bp.route("/login", methods=['POST'])
def login():
    try:
        credentials = request.json
        email = credentials['email']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': "Invalid payload expecting username and password."}), 400
    
    query = select(Member).where(Member.email == email)
    member = db.session.execute(query).scalars().first()

    if member and member.password == password: #if we have a user associated with the username, validate the password
        auth_token = encode_token(member.id, member.role.role_name)

        response = {
            "status": "success",
            "message": "Successfully Logged In",
            "auth_token": auth_token
        }
        return jsonify(response), 200
    else:
        return jsonify({'messages': "Invalid email or password"}), 401




@members_bp.route("/members", methods=['POST'])
@limiter.limit("3 per hour")
@cache.cached(timeout=60)
def create_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages),400
    


    query = select(Member).where(Member.email == member_data['email'])
    existing_member = db.session.execute(query).scalars().all()
    if existing_member:
        return jsonify({"error": "Email already associated with an account."}), 400
    
    new_member = Member(**member_data)
    db.session.add(new_member)
    db.session.commit()
    return member_schema.jsonify(new_member), 201


#GET ALL MEMBERS
@members_bp.route("/members", methods=['GET'])
def get_members():
    query = select(Member)
    members = db.session.execute(query).scalars().all()

    return members_schema.jsonify(members)

#GET SPECIFIC MEMBER
@members_bp.route("/members/<int:member_id>", methods=['GET'])
def get_member(member_id):
    member = db.session.get(Member, member_id)

    if member:
        return member_schema.jsonify(member), 200
    return jsonify({"error": "Member not found."}), 404


#UPDATE SPECIFIC USER
@members_bp.route("/members/<int:member_id>", methods=['PUT'])
def update_member(member_id):
    member = db.session.get(Member, member_id)

    if not member:
        return jsonify({"error": "Member not found."}), 404
    
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in member_data.items():
        setattr(member, key, value)

    db.session.commit()
    return member_schema.jsonify(member), 200


#DELETE SPECIFIC MEMBER
@members_bp.route("/", methods=['DELETE'])
@token_required
def delete_member(member_id):
    query = select(Member).where(Member.id == member_id)
    member = db.session.execute(query).scalars().first()

    if not member:
        return jsonify({"error": "Member not found."}), 404
    
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": f'Member id: {member_id}, successfully deleted.'}), 200
