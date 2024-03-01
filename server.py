"""
Simple contacts web app using flask and sqlite3 database to store the contacts
"""

from secrets import token_hex

from flask import Flask, redirect, render_template, request, session

import db_con

app = Flask(__name__)
app.secret_key = db_con.SECRET_KEY


@app.route("/", methods=["GET"])
def home_page():
    """
    The home page with request method
    """
    session.pop("user_unique_id", None)
    session.pop("user_name", None)

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])  # type: ignore
def login_page():
    """
    The login page with the request method GET and POST and the login credentials
    It has following features:
    1. If the user is already logged in then it redirects to the contacts page
    2. If the user is not logged in then it redirects to the login page
    3. If the user is not logged in and the login credentials are wrong then it shows the error
    4. Stores the user data in the session
    """

    if request.method == "GET":
        user_unique_id = session.get("user_unique_id")
        user_name = session.get("user_name")

        if user_unique_id is not None:
            return redirect("/contacts")

        return render_template("login.html", login_error="")

    if request.method == "POST":
        user_email = request.form.get("email")
        user_password = request.form.get("password")

        if user_email == "" or user_password == "":
            return render_template(
                "login.html", login_error="User email or password cannot be empty"
            )

        login_cred = DB_CON.user_login_with_user_email(user_email, user_password)  # type: ignore

        if login_cred is None:
            return render_template("login.html", login_error="Wrong login credentials")

        user_unique_id = login_cred[0]
        user_name = login_cred[1]
        user_email = login_cred[2]

        session["user_unique_id"] = user_unique_id
        session["user_name"] = user_name

        return redirect("/contacts")


@app.route("/signup", methods=["GET", "POST"])  # type: ignore
def signup_page():
    """
    The signup page with the request method GET and POST and the signup credentials
    It has following features:
    1. If the user is already logged in then it redirects to the contacts page
    2. If the user is not logged in then it redirects to the signup page
    3. If the user is not logged in and the signup credentials are wrong then it shows the error
    4. Checks whether the user_email already exists in the database
    5. Stores the user data in the session
    """

    user_unique_id = session.get("user_unique_id")
    user_name = session.get("user_name")

    if request.method == "GET":
        if user_unique_id is not None:
            return redirect("/contacts")

        return render_template("signup.html", signup_error="")

    if request.method == "POST":
        user_name = request.form.get("name")
        user_email = request.form.get("email")
        user_password = request.form.get("password")

        if user_email == "" or user_password == "":
            return render_template(
                "signup.html", signup_error="Email or password cannot be empty"
            )

        if DB_CON.check_whether_user_email_exists(user_email):  # type: ignore
            return render_template("signup.html", signup_error="Email already exists")

        user_unique_id = token_hex(5)

        session["user_unique_id"] = user_unique_id
        session["user_name"] = user_name

        DB_CON.user_signup_with_user_email(
            user_unique_id, user_name, user_email, user_password
        )  # type: ignore
        return redirect("/contacts")


@app.route("/contacts", methods=["GET", "POST"])  # type: ignore
def contacts_page():
    """The contacts page with the user_name of the user and all the contacts displayed"""

    user_unique_id = session.get("user_unique_id")
    user_name = session.get("user_name")

    if request.method == "GET":
        if user_unique_id is None:
            return redirect("/login")

        all_contacts = DB_CON.get_all_contacts_of_user(user_unique_id)
        return render_template(
            "contacts.html", user_name=user_name, all_contacts=all_contacts
        )

    if request.method == "POST":
        contact_name = request.form.get("name")
        contact_number = request.form.get("number")

        if contact_name == "" or contact_number == "":
            return redirect("/contacts")

        contact_unique_id = token_hex(5)
        contact_number = int(contact_number)  # type: ignore
        DB_CON.user_save_contact(
            contact_unique_id, contact_name, contact_number, user_unique_id
        )  # type: ignore

        return redirect("/contacts")


@app.route("/logout")
def user_logout():
    """User logout function which pops the session data and redirects to the home page"""

    session.pop("user_unique_id", None)
    session.pop("user_name", None)

    return redirect("/")


@app.route("/update", methods=["GET", "POST"])  # type: ignore
def update_contact_of_user():
    """
    The update page with user_name as the parameter
    """

    if request.method == "GET":
        contact_id = request.args.get("contact_id", "")
        contact_name, contact_number = DB_CON.get_contact_from_contact_id(contact_id)

        return render_template(
            "update.html",
            contact_id=contact_id,
            contact_name=contact_name,
            contact_number=contact_number,
        )

    if request.method == "POST":
        contact_id = request.form.get("contact_id", "")
        new_contact_name = request.form.get("contact_name", "")
        new_contact_number = int(request.form.get("contact_number", "0"))

        DB_CON.update_contact_of_user(contact_id, new_contact_name, new_contact_number)

        return redirect("/contacts")


@app.route("/delete", methods=["POST"])
def delete_data():
    """
    The delete function which deletes the contact of the user
    """
    contact_id = request.form.get("contact_id", "")

    DB_CON.delete_contact(contact_id)

    return redirect("/contacts")


# def get_user_unique_id_from_data(user_name, user_email, user_password):
#     """
#     Generate the unique id for the credentials
#     """
#     return hashlib.md5((user_name + user_email + user_password).encode()).hexdigest()

# def get_hash_from_user_password(user_password: str) -> str:
#     """
#     Get the hash from the user_password

#     Args:
#         user_password (str): The user_password of the user

#     Returns:
#         str: The hash of the user_password
#     """
#     return hashlib.sha256(user_password.encode()).hexdigest()

print("[+] Connecting to the database")

DB_CON = db_con.ConnectionClass()
if DB_CON.check_the_connection():
    print("[+] Connected to the database")

    if __name__ == "__main__":
        app.run(debug=True, host="0.0.0.0", port=5000)

else:
    print("[+] Error connecting to the database")
