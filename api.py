from flask import Flask, make_response, request, jsonify
from flask_httpauth import HTTPBasicAuth
from flask_mysqldb import MySQL

#-----------------------------------------------------------------
app = Flask(__name__)


app.config["MYSQL_HOST"] = "localhost"

app.config["MYSQL_USER"] = "root"  

app.config["MYSQL_PASSWORD"] = "root"  

app.config["MYSQL_DB"] = "names"

app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route("/")
def hello_world():
    return "<p>Hello World!</p>"


#-------------------------------------------------------------------

auth = HTTPBasicAuth()
users = {  
    "cat": "secret123",
    
}


@auth.verify_password
def verify_password(username, password):
    if username in users and users[username] == password:
        return username


@auth.error_handler
def unauthorized():
    return make_response(jsonify({"message": "Unauthorized access"}), 401)


#-----------------------------------------------------------------

@app.route("/persons", methods=["GET"])
@auth.login_required
def get_persons():
    cur = mysql.connection.cursor()
    query = "SELECT * FROM persons"
    cur.execute(query)
    data = cur.fetchall()
    cur.close()

    return make_response(jsonify(data), 200)


#-----------------------------------------------------------------


@app.route("/persons/<int:id>", methods=["GET"])
@auth.login_required
def get_person_by_id(id):
    cur = mysql.connection.cursor()
    query = "SELECT * FROM persons WHERE id = %s"
    cur.execute(query, (id,))
    data = cur.fetchone()
    cur.close()

    if data:
        return make_response(jsonify(data), 200)
    else:
        return make_response(jsonify({"message": "Person not found"}), 404)


#-----------------------------------------------------------------


@app.route("/persons", methods=["POST"])
@auth.login_required
def add_person():
    cur = mysql.connection.cursor()
    info = request.get_json()
    name = info.get("name")
    age = info.get("age")

    if not name or not age:
        return make_response(jsonify({"message": "Missing required fields"}), 400)

    query = "INSERT INTO persons (name, age) VALUES (%s, %s)"
    cur.execute(query, (name, age))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()

    return make_response(jsonify({"message": "Person added successfully",
                                 "rows_affected": rows_affected}), 201)


#-----------------------------------------------------------------



@app.route("/persons/<int:id>", methods=["PUT"])
@auth.login_required
def update_person(id):
    cur = mysql.connection.cursor()
    info = request.get_json()
    name = info.get("name")
    age = info.get("age")

    if not name or not age:
        return make_response(jsonify({"message": "Missing required fields"}), 400)

    query = "UPDATE persons SET name = %s, age = %s WHERE id = %s"
    cur.execute(query, (name, age, id))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()

    if rows_affected > 0:
        return make_response(jsonify({"message": "Person updated successfully",
                                 "rows_affected": rows_affected}), 200)
    else:
        return make_response(jsonify({"message": "Person not found"}), 404)


#-----------------------------------------------------------------


@app.route("/persons/<int:id>", methods=["DELETE"])
@auth.login_required 
def delete_person(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM persons WHERE id = %s", (id,))
    mysql.connection.commit()
    rows_affected = cur.rowcount
    cur.close()

    return make_response(jsonify({"message": "Person deleted successfully",
                                 "rows_affected": rows_affected}), 200)

if __name__ == "__main__":
    app.run(debug=True)