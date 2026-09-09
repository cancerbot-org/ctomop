"""Emit a staging Blueprint using the verified existing web name and region.

No credentials are read. Existing web secrets/database settings stay in Render;
the worker references those settings rather than generating replacements.
"""
import argparse
import copy
from pathlib import Path

import yaml


def blueprint(web_name, region):
    production = yaml.safe_load((Path(__file__).resolve().parents[1] / 'render.yaml').read_text())
    web = copy.deepcopy(next(s for s in production['services'] if s['type'] == 'web'))
    worker_name, broker_name = f'{web_name}-worker', f'{web_name}-redis'
    web.update(name=web_name, branch='dev', region=region)
    # Reuse the existing staging values, including DATABASE_URL. Never create a
    # fresh database or signing keys when adopting an existing web service.
    for env in web['envVars']:
        if 'generateValue' in env or 'fromDatabase' in env:
            key = env['key']
            env.clear()
            env.update(key=key, sync=False)
    broker = {'name': broker_name, 'type': 'keyvalue', 'property': 'connectionString'}
    for env in web['envVars']:
        if env['key'] == 'CELERY_BROKER_URL':
            env.clear()
            env.update(key='CELERY_BROKER_URL', fromService=broker)
    web['envVars'].extend([
        {'key': 'ANTHROPIC_API_KEY', 'sync': False},
        {'key': 'CELERY_RESULT_BACKEND', 'fromService': broker},
    ])
    shared_keys = ('SECRET_KEY', 'DATABASE_URL', 'AUDIT_HMAC_KEY',
                   'EXPORT_SIGNING_KEY', 'ANTHROPIC_API_KEY')
    worker = {
        'type': 'worker', 'name': worker_name, 'runtime': 'python',
        'repo': web['repo'], 'branch': 'dev', 'region': region,
        'autoDeploy': True, 'plan': '1c-2g',
        'buildCommand': 'pip install -r requirements.txt',
        'startCommand': 'bash start-worker.sh',
        'envVars': [
            {'key': key, 'fromService': {'name': web_name, 'type': 'web', 'envVarKey': key}}
            for key in shared_keys
        ] + [
            {'key': 'PYTHON_VERSION', 'value': '3.12.0'},
            {'key': 'DEBUG', 'value': 'False'},
            {'key': 'CELERY_BROKER_URL', 'fromService': broker},
            {'key': 'CELERY_RESULT_BACKEND', 'fromService': broker},
            {'key': 'CELERY_WORKER_CONCURRENCY', 'value': '1'},
            {'key': 'CELERY_WORKER_PREFETCH_MULTIPLIER', 'value': '1'},
        ],
    }
    return {'services': [web, worker, {
        'type': 'keyvalue', 'name': broker_name, 'region': region,
        'plan': '256mb', 'ipAllowList': [], 'maxmemoryPolicy': 'noeviction',
    }]}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--web-service', required=True, help='Existing staging Render web service name')
    parser.add_argument('--region', required=True, choices=('oregon', 'ohio', 'virginia', 'frankfurt', 'singapore'))
    args = parser.parse_args()
    print(yaml.safe_dump(blueprint(args.web_service, args.region), sort_keys=False), end='')
