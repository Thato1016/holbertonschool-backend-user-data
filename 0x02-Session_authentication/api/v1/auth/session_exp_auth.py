#!/usr/bin/env python3
"""
Add an expiration date to a Session ID.
"""
from api.v1.auth.session_auth import SessionAuth
from os import getenv
from datetime import datetime as d


class SessionExpAuth(SessionAuth):
    """
    Add an expiration date to a Session ID.
    """
    def __init__(self):
        """
        Initializes the class.
        """
        SESSION_DURATION = getenv('SESSION_DURATION')
        if not SESSION_DURATION or type(SESSION_DURATION) is not int:
            self.session_duration = 0
        self.session_duration = int(SESSION_DURATION)

    def create_session(self, user_id=None):
        """
        Create a Session ID.
        """
        created_at = d.now()
        session_dict = {"user_id": user_id, "created_at": created_at}

        session_id = super().create_session(user_id)
        if session_id is None:
            return None
        self.user_id_by_session_id[session_id] = session_dict
        return session_id

    def user_id_for_session_id(self, session_id=None):
        """
        Return user_id from a session dictionary.
        """
        if session_id is None or \
                not self.user_id_by_session_id.has_key(session_id):
            return None
        if self.session_duration <= 0:
            return "user_id"
        if not self.session_dic.has_key(created_at):
            return None
        if (self.session_dic.get(created_at) + session_duration) < d.now:
            return None
        return self.session_dic.get('user_id')
