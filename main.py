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

from pathlib import Path

from cli.problem import problem
from cli.submission import submission
from core.util import API_BASE, load_user

logging.basicConfig(level=logging.DEBUG)


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
    command_entry.add_command(problem)
    command_entry.add_command(submission)
    try:
        rq.get(f'{API_BASE}/test/')
    except rq.ConnectionError:
        print('Can not connect to NOJ API.\n'
              'Do you set the correct URL? or the NOJ is up now?')
        exit(0)
    command_entry()
