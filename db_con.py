"""The database connection class for the contacts database"""

from datetime import date
from os import environ
from re import Match, search
from typing import Any, Optional, Sequence

from sqlalchemy import URL, Engine, Row, TextClause, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Loading the ca.pem file
with open("ca.pem", "w", encoding="utf-8") as file:
    file.write(environ.get("CERTIFICATE", ""))

SECRET_KEY: str = environ.get("SECRET_KEY", "")

url_object: URL = URL.create(
    drivername="mysql",
    username=environ.get("DBUSER"),
    password=environ.get("DBPASSWORD"),
    host=environ.get("DBHOST"),
    port=int(environ.get("DBPORT", 0)),
    database=environ.get("DBNAME"),
)


class ConnectionClass:
    """
    This is the class for the contacts database
    """

    def __init__(self):
        try:
            self.__engine: Optional[Engine] = create_engine(
                url_object,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=3600,
                pool_pre_ping=True,
                connect_args={"autocommit": True, "ssl": {"ssl_ca": "ca.pem"}},
            )

            # Database pool warmup successfully
            result: Optional[Match[str]] = search(r"Pool size: (\d+)", self.__engine.pool.status())
            if result is not None:
                for _ in range(int(result.group(1))):
                    self.__engine.connect().close()

        except SQLAlchemyError as error_name:
            print("[+] Error", error_name)
            self.__engine = None

    def check_the_connection(self) -> bool:
        """Returns True if the connection is established else False"""

        return bool(self.__engine)

    def close_connection(self) -> None:
        """Close the connection to the database"""

        if self.__engine is not None:
            self.__engine.dispose()

            print("[+] Connection to the database closed")

    def user_login_with_user_email(self, email: str, password: str) -> Optional[Row[Any]]:
        """Returns the user data if the user exists in the database"""

        if self.__engine is not None:
            with self.__engine.connect() as conn:
                stmt: TextClause = text("select lid, lname, lemail from login where lemail=:email and lpassword=:password")
                return conn.execute(stmt, {"email": email, "password": password}).fetchone()

        return None

    def check_whether_user_email_exists(self, email: str) -> bool:
        """Returns True if the email exists in the database else False"""

        if self.__engine is not None:
            with self.__engine.connect() as conn:
                stmt: TextClause = text("select lid from login where lemail=:email")
                return bool(conn.execute(stmt, {"email": email}).fetchone())

        return False

    def user_signup_with_user_email(self, unique_id: str, name: str, email: str, password: str) -> bool:
        """Function to signup the user with the email and password"""

        try:
            if self.__engine is not None:
                with self.__engine.connect() as conn:
                    stmt: TextClause = text("insert into login values (:lid, :lname, :lemail, :lpassword)")
                    conn.execute(
                        stmt,
                        {
                            "lid": unique_id,
                            "lname": name,
                            "lemail": email,
                            "lpassword": password,
                        },
                    )
                    conn.commit()
                return True

            return False

        except SQLAlchemyError:
            return False

    def user_save_contact(self, contact_id: str, name: str, number: int, user_id: str) -> None:
        """
        Put name and number into the database
        """
        if self.__engine is not None:
            with self.__engine.connect() as conn:
                stmt: TextClause = text("insert into contact values (:cid, :cname, :cnumber, :lid, :date)")
                conn.execute(
                    stmt,
                    {
                        "cid": contact_id,
                        "cname": name,
                        "cnumber": number,
                        "lid": user_id,
                        "date": date.today(),
                    },
                )
                conn.commit()

    def get_all_contacts_of_user(self, user_id: str) -> Sequence[Row[Any]]:
        """
        Get all the data from the database and return it

        Returns:
            list: The list of all the data
        """
        if self.__engine is not None:
            with self.__engine.connect() as conn:
                stmt: TextClause = text("select cid, cname, cnumber from contact where lid=:lid")
                return conn.execute(stmt, {"lid": user_id}).fetchall()

        return []

    def delete_contact(self, contact_id: str) -> None:
        """
        Delete the contact of the user from the database from the name

        Args:
            contact_id (str): The id of the contact
        """
        if self.__engine is not None:
            with self.__engine.connect() as conn:
                stmt: TextClause = text("delete from contact where cid=:cid")
                conn.execute(stmt, {"cid": contact_id})
                conn.commit()

    def get_contact_from_contact_id(self, contact_id: str) -> Optional[Row[Any]]:
        """
        Get the contact from the contact id

        Args:
            contact_id (str): The contact id of the contact

        Returns:
            tuple: The contact data (cid, cname, cnumber)
        """
        if self.__engine is not None:
            with self.__engine.connect() as conn:
                stmt: TextClause = text("select cname, cnumber from contact where cid=:cid")
                return conn.execute(stmt, {"cid": contact_id}).fetchone()

        return None

    def update_contact_of_user(
        self,
        contact_id: str,
        new_contact_name: str,
        new_contact_number: int,
    ) -> None:
        """
        Update the details of the contact in the database from the name and user unique id

        Args:
            contact_id (str): The id of the contact
            new_contact_number (int): The new number of the contact
            contact_name (str): The name of the contact
        """

        if self.__engine is not None:
            with self.__engine.connect() as conn:
                stmt: TextClause = text("update contact set cname=:cname, cnumber=:cnumber where cid=:cid")
                conn.execute(
                    stmt,
                    {
                        "cid": contact_id,
                        "cnumber": new_contact_number,
                        "cname": new_contact_name,
                    },
                )
                conn.commit()
