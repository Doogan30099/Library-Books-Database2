from datetime import datetime, timedelta, timezone
from jose import jwt
from functools import wraps, jwt
import jose.exceptions
from flask import request, jsonify

SECRET_KEY = "a super secret key"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        #look for the token in the authorization header 
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401


        try:
            #decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            member_id = data['sub']


        except jose.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jose.exceptions.JwtError:
            return jsonify({'message': 'Invalid token!'}), 401
        
        return f(member_id, *args, **kwargs)
    return decorated 



def encode_token(member_id):
    payload = {"exp": datetime.now(timezone.utc) + timedelta(days=0, hours=1),
               "iat": datetime.now(timezone.utc),
               "sub": str(member_id)}

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token 