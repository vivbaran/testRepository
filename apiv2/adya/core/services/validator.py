from flask_restful import Resource, reqparse, request

def validate_flask_auth_token(request):
    if request.method != 'OPTIONS':
        auth_token = request.headers.get('Authorization')
        if not auth_token:
            return {'message': 'Missing auth token'}, 400