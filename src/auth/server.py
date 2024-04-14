import jwt, datetime, os
from flask import Flask, request, jsonify
from flask_mysqldb import MySQL

app = Flask(__name__)

mysql = MySQL(app)

# MySQL configurations
app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = os.environ.get("MYSQL_DATABASE")
app.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))

# Create a JWT token
def createJWT(username: str, secret: str, authz: bool = False):
    return jwt.encode(
        {
            "user": username, 
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1), 
            "iat": datetime.datetime.utcnow(),
            "admin": authz
        }, 
        secret,
        algorithm="HS256"
    )

@app.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return jsonify({"message": "Could not verify", "WWW-Authenticate": "Basic auth='Login required'"}), 401
    
    # Check if the user exists
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", [auth.username])
    user = cur.fetchone()

    if not user:
        return jsonify({"message": "User not found"}), 401
    
    if user[2] == auth.password:
        token = createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
        return jsonify({"token": token})
    
    return jsonify({"message": "Could not verify", "WWW-Authenticate": "Basic auth='Login required'"}), 401


@app.route("/validate", methods=["POST"])
def validate():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"message": "Token is missing"}), 401
    
    try:
        data = jwt.decode(token.split(" ")[1], os.environ.get("JWT_SECRET"), algorithms=["HS256"])
        return jsonify(data)
    except:
        return jsonify({"message": "Token is invalid"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)