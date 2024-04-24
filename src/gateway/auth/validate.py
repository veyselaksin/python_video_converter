import os, requests

def token(request):
    if not request.headers.get("Authorization"):
        return {"message": "Token is missing"}, 401
    
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate", 
        headers={"Authorization": request.headers.get("Authorization")}
    )

    if response.status_code != 200:
        return {"message": "Token is invalid"}, 401
    
    return response.json(), 200
