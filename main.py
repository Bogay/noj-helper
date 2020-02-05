import requests as rq
import json
import sys
import random
import string
import secrets

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
    print('===submission===')
    langs = ['c', 'cpp', 'py']

    # create submission
    resp = sess.post(
        f'{API_BASE}/submission',
        json={
            'languageType': lang,
            'problemId': problem_id
        },
    )
    rj = json.loads(resp.text)
    print(rj)
    rj = rj['data']
    assert resp.status_code == 200

    # upload source
    resp = sess.put(
        f'{API_BASE}/submission/{rj["submissionId"]}?token={rj["token"]}',
        files={
            'code': ('scnuoqd414fwq', open(f'{langs[lang]}-code.zip', 'rb'))
        },
    )
    print(resp.status_code)
    print(resp.text)
    assert resp.status_code == 200
    print('===end===')


def create_problem(sess, **prob_datas):
    print('===problem===')
    resp = sess.post(
        f'{API_BASE}/problem/manage',
        json={
            'courses':
            prob_datas.get(
                'courses',
                ['Public'],
            ),
            'status':
            prob_datas.get(
                'status',
                0,
            ),
            'type':
            prob_datas.get(
                'type',
                0,
            ),
            'problemName':
            prob_datas.get('problem_name', 'A + B problem'),
            'description':
            prob_datas.get('description') or open('prob.md').read(),
            'tags':
            prob_datas.get(
                'tags',
                ['test'],
            ),
            'testCase':
            prob_datas.get(
                'testCase',
                {
                    'language':
                    0,
                    'fillInTemplate':
                    '',
                    'cases': [
                        {
                            'input': '14 50\n',
                            'output': '64\n',
                            'caseScore': 100,
                            'memoryLimit': 32768,
                            'timeLimit': 1000,
                        },
                    ]
                },
            )
        },
    )
    print(resp.status_code)
    print(resp.text)
    assert resp.status_code == 200
    print('===end===')


def get_problem_list(sess, offset, count):
    resp = sess.get(
        f'{API_BASE}/problem?offset={offset}&count={count}&problemId=2')
    print(resp.status_code)
    print(resp.text)
    assert resp.status_code == 200


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) >= 2 else None
    user = {
        'username': 'first_admin',
        'password': 'firstpasswordforadmin',
        'email': 'i.am.first.admin@noj.tw'
    }
    # user = {
    #     'username': 'bogay',
    #     'password': 'bogay',
    # }

    if cmd is None:
        with login_session(**user) as sess:
            submit(sess, 0, 4)
    elif cmd == 'prob':
        with login_session(**user) as sess:
            create_problem(sess)
    elif cmd == 'prob-list':
        with login_session(**user) as sess:
            get_problem_list(sess, 0, -1)
