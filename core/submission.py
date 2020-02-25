import logging
import requests as rq
import json
from zipfile import is_zipfile
from .util import API_BASE


def submit(sess, lang, problem_id, code=None):
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