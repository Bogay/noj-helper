import click
from core.util import login_session
from core.submission import submit as submit_action


@click.group()
def submission():
    '''
    functions about submission
    '''


@submission.command()
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
        submit_action(sess, language, problem_id, code)