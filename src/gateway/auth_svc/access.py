import os, requests

def login(request):
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return {"message": "Could not verify", "WWW-Authenticate": "Basic auth='Login required'"}, 401
    
    # Check if the user exists
    user = requests.post(f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login", auth=(auth.username, auth.password))
    if user.status_code != 200:
        return {"message": "User not found"}, 401
    
    return user.json(), 200