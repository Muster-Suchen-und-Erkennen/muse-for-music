from json import loads
from flask import Flask
from flask.testing import FlaskClient
from util import get_hateoas_resource, try_self_link, AuthActions


def test_api_root(client: FlaskClient, auth: AuthActions, app: Flask):
    result = get_hateoas_resource(client)
    assert result.status_code == 200
    object = result.get_json()
    try_self_link(object, client)
    for rel in object['_links']:
        if rel == 'self' or rel == 'curies':
            continue
        link_result = get_hateoas_resource(client, rel, root=object)
        assert link_result.status_code in (200, 401), 'Failed to load rel "{}"'.format(rel)
        if link_result.status_code == 401:
            token = auth.login('admin', 'admin').get_json()['access_token']
            link_result = get_hateoas_resource(client, rel, root=object, auth=token)
            assert link_result.status_code == 200


def test_api_doc(client: FlaskClient, app: Flask):
    result = get_hateoas_resource(client, 'doc')
    assert result.status_code == 200
