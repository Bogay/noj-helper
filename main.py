#!.venv/bin/python
import requests as rq
import json
import sys
import random
import string
import secrets
import logging
import click
import csv
import tempfile

from pathlib import Path
from zipfile import ZipFile, is_zipfile

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
        logging.error(resp.text)
        return None
    return sess


def _submit(sess, lang, problem_id, code=None):
    '''
    submit `problem_id` with language `lang`
    if `code` is None, use default source decided by `lang`

    Args:
        code: the code path
    '''
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

    # open code file
    if code is None:
        # use default
        code = open(f'{langs[lang]}-code.zip', 'rb')
    else:
        # check zip
        if not is_zipfile(code):
            logging.warning('you are submitting a non-zip file.')
        # if it is the path string
        if 'read' not in code:
            code = open(code, 'rb')

    # upload source
    resp = sess.put(
        f'{API_BASE}/submission/{rj["submissionId"]}',
        files={'code': ('scnuoqd414fwq', code)},
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
    return {
        'language':
        0,
        'fillInTemplate':
        '',
        'tasks': [
            {
                'caseScore': 100,
                'caseCount': 1,
                'memoryLimit': 32768,
                'timeLimit': 1000,
            },
        ]
    }


def make_testcase_zip(tasks=[1]) -> tempfile.TemporaryFile:
    '''
    make a dummy testcase zip file

    Args:
        tasks: list contains case count for each task
    '''
    tmp_zip = tempfile.TemporaryFile('wb+')
    with ZipFile(tmp_zip, 'w') as zf:
        for i, cnt in enumerate(tasks):
            for j in range(cnt):
                name = f'{i:02d}{j:02d}'
                v = random_string(48)
                zf.writestr(f'{name}.in', v)
                zf.writestr(f'{name}.out', v)
    tmp_zip.seek(0)
    return tmp_zip


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
    logging.info('===upload testcase===')
    problem_id = json.loads(resp.text)['data']['problemId']
    with make_testcase_zip() as test_case:
        resp = sess.put(
            f'{API_BASE}/problem/manage/{problem_id}',
            files={
                'case': ('test_case', test_case),
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
@click.option(
    '--code',
    '-c',
    help='the code path which will be submitted',
)
@click.pass_obj
def submit(ctx_obj, language, problem_id, code):
    with login_session(**ctx_obj['user']) as sess:
        _submit(sess, language, problem_id, code)


@command_entry.command()
@click.pass_obj
def prob(ctx_obj):
    with login_session(**ctx_obj['user']) as sess:
        create_problem(sess)


@command_entry.command()
@click.argument('users')
def create_user(users):
    '''
    create users from file
    '''
    users = Path(users)
    if not users.exists():
        print(f'{users} not found!')
        return

    if users.suffix == '.csv':
        with open(users) as f:
            _users = csv.DictReader(f)
        users = _users
    elif users.suffix == '.json':
        users = json.loads(users.read_text())
    elif users.suffix == '.xls':
        print('haven\'t implemented')
        return

    for u in users:
        rq.post(f'{API_BASE}/auth/signup', json=u)


if __name__ == "__main__":
    try:
        admin = load_user('first_admin')
        with login_session(**admin) as sess:
            pass
    except rq.ConnectionError:
        print('Can not connect to NOJ API.\n'
              'Do you set the correct URL? or the NOJ is up now?')
        exit(0)
    command_entry()
