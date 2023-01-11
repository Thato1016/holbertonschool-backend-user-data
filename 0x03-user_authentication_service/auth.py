#!/usr/bin/env python3
"""
This module contains the methods and attributes needed
for the authentication
"""
from bcrypt import hashpw, gensalt, checkpw
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
import uuid


class Auth:
    """Auth class to interact with the authentication database.
    """
    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Registers a user in database.
        Args:
            email: A non-nullable string.
            password: A non-nullable string.
        Raises:
            ValueError: User already exists.
        Returns:
            User: User object.
        """
        try:
            users_found = self._db.find_user_by(email=email)
            if users_found:
                raise ValueError("User {} already exists".format(email))
        except NoResultFound:
            hashed_password = _hash_password(password).decode('utf-8')
            user = self._db.add_user(email, hashed_password)
            return user

    def valid_login(self, email: str, password: str) -> bool:
        """
        Login method.
        Args:
            email: A non-nullable string.
            password: A non-nullable string.
        Returns:
            bool: True if login, False otherwise.
        """
        if not email or not password:
            return False
        try:
            users_found = self._db.find_user_by(email=email)
            hashed_password = users_found.hashed_password
            return checkpw(password.encode(),
                           hashed_password.encode('utf-8'))
        except (NoResultFound, InvalidRequestError):
            return False

    def create_session(self, email: str) -> Union[str, None]:
        """
        Create Session.
        Takes an email string argument and returns the session ID as a string.
        Args:
            email: A non-nullable string.
        Returns:
            str: The session id.
        """
        try:
            user = self._db.find_user_by(email=email)
            session_id = _generate_uuid()
            self._db.update_user(user.id, session_id=session_id)
            return session_id
        except (NoResultFound, ValueError):
            return None

    def get_user_from_session_id(self, session_id: str) -> Union[User, None]:
        """
        Get user from a session id.
        Takes a single session_id string argument
        and returns the corresponding User or None.
        Args:
            session_id: The session id.
        Returns:
            User: The user object, None otherwise.
        """
        if not session_id:
            return None
        try:
            user = self._db.find_user_by(session_id=session_id)
            return user
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """
        Destroys a session.
        Takes a single session_id string argument
        and returns the corresponding User or None.
        Args:
            user_id: The user id.
        """
        try:
            self._db.update_user(user_id, session_id=None)
        except ValueError:
            pass

    def get_reset_password_token(self, email: str) -> str:
        """
        Get a reset password.
        Takes an email string argument and returns a string.
        Args:
            email: A non-nullable string.
        Raises:
            ValueError: User does not exist.
        Returns:
            str: The reset password token.
        """
        try:
            user = self._db.find_user_by(email=email)
            if user.reset_token:
                return user.reset_token
            token = _generate_uuid()
            self._db.update_user(user.id, reset_token=token)
            return token
        except NoResultFound:
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Updates password.
        Takes reset_token string argument and a password string argument
        and returns None.
        Args:
            reset_token: Reset password token.
            password: New password.
        Returns:
            bool: True if password was updated, False otherwise.
        Raises:
            ValueError: If the reset token is invalid.
        """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashed_password = _hash_password(password).decode('utf-8')
            self._db.update_user(user.id, hashed_password=hashed_password,
                                 reset_token=None)
        except NoResultFound:
            raise ValueError


def _hash_password(password: str) -> bytes:
    """
    Takes in a password string arguments and returns bytes.
    Args:
        password: The password to be encrypted.
    Returns:
        bytes: Salted hash of the input password, hashed with bcrypt.hashpw.
    """
    return hashpw(password.encode(), gensalt())


def _generate_uuid() -> str:
    """
    Return a string representation of a new UUID.
    Returns:
        str: The generated UUID.
    """
    return str(uuid.uuid4())
