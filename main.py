#!.venv/bin/python
import requests as rq
import json
import sys
import random
import string
import secrets
import logging
import click

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


def _submit(sess, lang, problem_id):
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
        f'{API_BASE}/submission/{rj["submissionId"]}'
        f'?token={rj["token"]}',
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
        f'{API_BASE}/problem'
        f'?offset={offset}'
        f'&count={count}'
        '&problemId=2', )
    logging.info(resp.status_code)
    logging.info(resp.text)
    assert resp.status_code == 200


def load_user(user) -> dict:
    with open(f'user/{user}.json') as f:
        return json.load(f)


@click.group()
@click.option(
    '--user',
    '-u',
    default='first_admin',
    help='which user to login',
)
@click.pass_context
def command_entry(ctx, user):
    '''
    the entry of noj cli(?
    '''
    ctx.ensure_object(dict)
    ctx.obj['user'] = load_user(user)


@command_entry.command()
@click.argument('problem_id', type=int)
@click.argument('language', type=int)
@click.pass_obj
def submit(ctx_obj, language, problem_id):
    with login_session(**ctx_obj['user']) as sess:
        _submit(sess, language, problem_id)


@command_entry.command()
@click.pass_obj
def prob(ctx_obj):
    with login_session(**ctx_obj['user']) as sess:
        create_problem(sess)


if __name__ == "__main__":
    try:
        admin = load_user('first_admin')
        with login_session(**admin) as sess:
            pass
    except rq.ConnectionError:
        print('Can not connect to NOJ API.\n'
              'Do you set the current URL? or the NOJ is up now?')
        exit(0)
    command_entry()
