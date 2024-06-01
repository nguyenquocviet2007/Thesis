import jwt
import os
from datetime import timedelta, datetime

def AccessToken(studentId, id, role):
        payload = {
                'id': id,
                'studentId': studentId,
                'role': role,
                'exp': datetime.now() + timedelta(minutes=180),
                'iat': datetime.now()
            } 
        access_token = jwt.encode(payload, os.environ.get('ACCESS_TOKEN'), algorithm='HS256')
        return access_token
 
def RefreshToken(studentId, id, role):
    payload = {
            'id': id,
            'studentId': studentId,
            'role': role,
            'exp': datetime.now() + timedelta(minutes=180),
            'iat': datetime.now()
        } 
    refresh_token = jwt.encode(payload, os.environ.get('REFRESH_TOKEN'), algorithm='HS256')
    return refresh_token


            