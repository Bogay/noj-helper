import logging
import tempfile
import requests as rq
import json
from zipfile import ZipFile
from .util import API_BASE, random_string


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
                'taskScore': 100,
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
            'problemName': prob_datas.get('problem_name') or 'A + B problem',
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