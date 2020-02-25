import requests as rq
import secrets
import json

# API_BASE = 'https://noj.tw/api'
API_BASE = 'http://localhost:8080/api'


def random_string(k=4):
    return secrets.token_urlsafe(k)


def login_session(username, password, email=None):
    sess = rq.Session()
    resp = sess.post(
        f'{API_BASE}/auth/session',
        json={
            'username': username,
            'password': password
        },
    )

    if resp.status_code != 200:
        sess.close()
        logging.error(resp.text)
        return None
    return sess


def load_user(user) -> dict:
    with open(f'user/{user}.json') as f:
        return json.load(f)