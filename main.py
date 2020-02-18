import requests as rq
import json
import sys
import random
import string
import secrets
import logging

logging.basicConfig(level=logging.DEBUG)

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
        return None
    return sess


def submit(sess, lang, problem_id):
    logging.info('===submission===')
    langs = ['c', 'cpp', 'py']

    # create submission
    resp = sess.post(
        f'{API_BASE}/submission',
        json={
            'languageType': lang,
            'problemId': problem_id
        },
    )

    logging.debug(f'raw resp: {resp.text}')
    rj = json.loads(resp.text)
    logging.info(rj)
    rj = rj['data']
    assert resp.status_code == 200

    # upload source
    resp = sess.put(
        f'{API_BASE}/submission/{rj["submissionId"]}?token={rj["token"]}',
        files={
            'code': ('scnuoqd414fwq', open(f'{langs[lang]}-code.zip', 'rb'))
        },
    )
    logging.info(resp.status_code)
    logging.info(resp.text)
    assert resp.status_code == 200
    logging.info('===end===')


def problem_description():
    return {
        'description': 'fake a + b problem',
        'input': 'test',
        'output': 'test',
        'sampleInput': ['foo'],
        'sampleOutput': ['bar'],
        'hint': 'hint',
    }


def problem_testcase():
    r = secrets.token_hex()
    return {
        'language':
        0,
        'fillInTemplate':
        '',
        'cases': [
            {
                'caseScore': 100,
                'caseCount': 1,
                'memoryLimit': 32768,
                'timeLimit': 1000,
                'input': [f'{r}\n'],
                'output': [f'{r}\n'],
            },
        ]
    }


def create_problem(sess, **prob_datas):
    logging.info('===problem===')
    resp = sess.post(
        f'{API_BASE}/problem/manage',
        json={
            'courses': prob_datas.get(
                'courses',
                ['Public'],
            ),
            'status': prob_datas.get(
                'status',
                0,
            ),
            'type': prob_datas.get(
                'type',
                0,
            ),
            'problemName': prob_datas.get(
                'problem_name',
                'A + B problem',
            ),
            'description': prob_datas.get(
                'description',
                problem_description(),
            ),
            'tags': prob_datas.get(
                'tags',
                ['test'],
            ),
            'testCaseInfo': prob_datas.get(
                'testCaseInfo',
                problem_testcase(),
            ),
            'handwritten': False,
        },
    )
    logging.info(resp.status_code)
    logging.info(resp.text)
    assert resp.status_code == 200
    logging.info('===end===')


def get_problem_list(sess, offset, count):
    resp = sess.get(
        f'{API_BASE}/problem?offset={offset}&count={count}&problemId=2')
    logging.info(resp.status_code)
    logging.info(resp.text)
    assert resp.status_code == 200


def load_user(user) -> dict:
    with open(f'user/{user}.json') as f:
        return json.load(f)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) >= 2 else None
    user = load_user('first_admin')

    if cmd is None:
        with login_session(**user) as sess:
            submit(sess, 1, 4)
    elif cmd == 'prob':
        with login_session(**user) as sess:
            create_problem(sess)
    elif cmd == 'prob-list':
        with login_session(**user) as sess:
            get_problem_list(sess, 0, -1)
