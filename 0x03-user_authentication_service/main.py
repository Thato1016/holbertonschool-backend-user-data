#!/usr/bin/env python3
"""
Query your web server for the corresponding end-point.
And validates the response’s expected status code and payload (if any).
"""
import requests


def register_user(email: str, password: str) -> None:
    """
    Registers a user in database.
    Args:
        email: A non-nullable string.
        password: A non-nullable string.
    """
    r = requests.post('http://127.0.0.1:5000/users',
                      data={'email': email, 'password': password})
    if r.status_code == 200:
        assert (r.json() == {"email": email, "message": "user created"})
    else:
        assert(r.status_code == 400)
        assert (r.json() == {"message": "email already registered"})


def log_in_wrong_password(email: str, password: str) -> None:
    """
    Login with wrong credentials.
    Args:
        email: A non-nullable string.
        password: A non-nullable string.
    """
    r = requests.post('http://127.0.0.1:5000/sessions',
                      data={'email': email, 'password': password})
    assert (r.status_code == 401)


def log_in(email: str, password: str) -> str:
    """
    Log in with correct credentials.
    Args:
        email: A non-nullable string.
        password: A non-nullable string.
    Returns:
        The session_id of the user.
    """
    r = requests.post('http://127.0.0.1:5000/sessions',
                      data={'email': email, 'password': password})
    assert (r.status_code == 200)
    assert(r.json() == {"email": email, "message": "logged in"})
    return r.cookies['session_id']


def profile_unlogged() -> None:
    """
    Profile without logging in with session_id.
    """
    r = requests.get('http://127.0.0.1:5000/profile')
    assert(r.status_code == 403)


def profile_logged(session_id: str) -> None:
    """
    Profile Logged.
    Args:
        session_id: The session_id of the user.
    """
    cookies = {'session_id': session_id}
    r = requests.get('http://127.0.0.1:5000/profile',
                     cookies=cookies)
    assert(r.status_code == 200)


def log_out(session_id: str) -> None:
    """
    Logout.
    Args:
        session_id: The session_id of the user.
    """
    cookies = {'session_id': session_id}
    r = requests.delete('http://127.0.0.1:5000/sessions',
                        cookies=cookies)
    if r.status_code == 302:
        assert(r.url == 'http://127.0.0.1:5000/')
    else:
        assert(r.status_code == 200)


def reset_password_token(email: str) -> str:
    """
    Reset password with email.
    Args:
        email: A non-nullable string.
    Returns:
        The token resetted.
    """
    r = requests.post('http://127.0.0.1:5000/reset_password',
                      data={'email': email})
    if r.status_code == 200:
        return r.json()['reset_token']
    assert(r.status_code == 401)


def update_password(email: str, reset_token: str,
                    new_password: str) -> None:
    """
    Update password with email, reset token and new password.
    Args:
        email: A non-nullable string.
        reset_token: Reset token.
        new_password: New password.
    """
    data = {'email': email, 'reset_token': reset_token,
            'new_password': new_password}
    r = requests.put('http://127.0.0.1:5000/reset_password',
                     data=data)
    if r.status_code == 200:
        assert(r.json() == {"email": email, "message": "Password updated"})
    else:
        assert(r.status_code == 403)


EMAIL = "guillaume@holberton.io"
PASSWD = "b4l0u"
NEW_PASSWD = "t4rt1fl3tt3"


if __name__ == "__main__":

    register_user(EMAIL, PASSWD)
    log_in_wrong_password(EMAIL, NEW_PASSWD)
    profile_unlogged()
    session_id = log_in(EMAIL, PASSWD)
    profile_logged(session_id)
    log_out(session_id)
    reset_token = reset_password_token(EMAIL)
    update_password(EMAIL, reset_token, NEW_PASSWD)
    log_in(EMAIL, NEW_PASSWD)
