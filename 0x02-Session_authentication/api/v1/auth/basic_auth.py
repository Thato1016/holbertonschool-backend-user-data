#!/usr/bin/env python3
"""
Module basic_auth
"""
from api.v1.auth.auth import Auth
from base64 import b64decode
from models.user import User
from typing import TypeVar


class BasicAuth(Auth):
    """
    Inherits from Auth
    """
    def extract_base64_authorization_header(self,
                                            authorization_header: str) -> str:
        """
        Returns the Base64 part of the Authorization header
        for a Basic Authentication
        """
        if not authorization_header or not type(authorization_header) == str:
            return None
        if not authorization_header.startswith('Basic '):
            return None
        return authorization_header[6:]

    def decode_base64_authorization_header(
            self, base64_authorization_header: str) -> str:
        """
        Returns decoded value of a Base64 string base64_authorization_header
        """
        if base64_authorization_header is None or not isinstance(
                base64_authorization_header, str):
            return None
        try:
            return b64decode(base64_authorization_header).decode('utf-8')
        except Exception as e:
            None

    def extract_user_credentials(
            self, decoded_base64_authorization_header: str) -> (str, str):
        """
        Returns the user email and password from the Base64 decoded value.
        """
        if not decoded_base64_authorization_header or\
                type(decoded_base64_authorization_header) != str or\
                ":" not in decoded_base64_authorization_header:
            return None, None
        values = decoded_base64_authorization_header.split(":")

        return values[0], ":".join(values[1:])

    def user_object_from_credentials(
            self, user_email: str, user_pwd: str) -> TypeVar('User'):
        """
        Returns a user instance based on his email and password.
        """
        if not user_email or\
                type(user_email) != str or\
                not user_pwd or\
                type(user_pwd) != str:
            return None
        try:
            users = User.search({'email': user_email})
        except Exception:
            return None
        for user in users:
            if user.is_valid_password(user_pwd):
                return user
            return None

    def current_user(self, request=None) -> TypeVar('User'):
        """
        Overloads Auth and retrieves the User instance for a request.
        """
        header = self.authorization_header(request)
        base64 = self.extract_base64_authorization_header(header)
        decoded = self.decode_base64_authorization_header(base64)
        credentials = self.extract_user_credentials(decoded)
        user = user = self.user_object_from_credentials(*credentials)

        return user
