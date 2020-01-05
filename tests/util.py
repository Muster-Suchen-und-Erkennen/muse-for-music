from hypothesis import assume, reject, strategies as st
from flask_restplus import fields, Model

from muse_for_music.api import api


def auth_header(token: str):
    if token:
        return {'Authorization': 'Bearer {}'.format(token)}
    return None


class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='admin', password='admin'):
        url = get_hateoas_ref(self._client, 'login', root='users')
        return self._client.post(url, json={'username': username, 'password': password})

    def logout(self):
        return self._client.get("/auth/logout")

    def add_role(self, role: str, username='admin', auth=None):
        assert role in {'user', 'admin', 'taxonomy_editor'}
        if auth is None:
            auth = self.login().get_json()['access_token']
        users_url = get_hateoas_ref(self._client, 'management', 'user', root='users', auth=auth)
        user = self._client.get('{}{}/'.format(users_url, username), headers=auth_header(auth)).get_json()
        roles_url = get_hateoas_ref(self._client, 'roles', root=user)
        result = self._client.post(roles_url, json={'role': role}, headers=auth_header(auth))
        assert result.status_code == 200


def api_model_strategy(model: str, api = api):
    m = api.models[model]
    return st.one_of(dict_model_example(m), dict_model_default(m), dict_model_strategy(m))


SKIP_MODEL_KEYS = {'id', '_links'}


def dict_model_example(model: Model):
    mapping = {}
    for key, value in model.resolved.items():
        if key in SKIP_MODEL_KEYS:
            continue
        mapping[key] = field_example_strategy(value)
    return st.fixed_dictionaries(mapping)


def dict_model_default(model: Model):
    mapping = {}
    for key, value in model.resolved.items():
        if key in SKIP_MODEL_KEYS:
            continue
        mapping[key] = field_default_strategy(value)
    return st.fixed_dictionaries(mapping)


def dict_model_strategy(model: Model):
    mapping = {}
    for key, value in model.resolved.items():
        if key in SKIP_MODEL_KEYS:
            continue
        mapping[key] = field_strategy(value)
    return st.fixed_dictionaries(mapping)


def field_example_strategy(field: fields.Raw):
    try:
        if field.example is not None:
            return st.just(field.example)
    except AttributeError:
        pass
    if isinstance(field, fields.Nested):
        return(st.deferred(lambda: dict_model_example(field.model)))
    return field_default_strategy(field)


def field_default_strategy(field: fields.Raw):
    try:
        if field.default is not None:
            return st.just(field.default)
    except AttributeError:
        pass
    if isinstance(field, fields.Nested):
        return(st.deferred(lambda: dict_model_default(field.model)))
    return field_strategy(field)


def field_strategy(field: fields.Raw):
    try:
        if field.enum is not None:
            return st.sampled_from(field.enum)
    except AttributeError:
        pass
    if isinstance(field, fields.String):
        return st.text(max_size=500)
    elif isinstance(field, fields.Integer):
        return st.integers()
    elif isinstance(field, fields.Nested):
        if 'x-reference' in field.extra_attributes:
            print(field.extra_attributes)
        return(st.deferred(lambda: dict_model_strategy(field.model)))
    return st.nothing()


# Model Strategies:

PERSON_POST = api_model_strategy('PersonPOST')
PERSON_PUT = api_model_strategy('PersonPUT')

OPUS_POST = api_model_strategy('OpusPOST')
OPUS_PUT = api_model_strategy('OpusPUT')


# Test methods

def get_hateoas_ref_from_object(object, rel: str):
    assert '_links' in object
    links = object['_links']
    assert rel in links
    url = links[rel]
    assert 'href' in url
    return url['href']


def get_hateoas_ref(client, *rels, auth=None, root='api'):
    url = ''
    if isinstance(root, str):
        url = '/{}/'.format(root)
    else:
        assert len(rels) > 0
        url = get_hateoas_ref_from_object(root, rels[0])
        rels = rels[1:]
    headers = auth_header(auth)
    for rel in rels:
        result = client.get(url, headers=headers)
        url = result.get_json()['_links'][rel]['href']
    return url


def get_hateoas_resource(client, *rels, auth=None, root='api'):
    headers = auth_header(auth)
    url = get_hateoas_ref(client, *rels, auth=auth, root=root)
    return client.get(url, headers=headers)


def try_self_link(object, client, auth=None):
    url = object['_links']['self']['href']
    result = client.get(url)
    assert result.status_code == 200
    obj2 = result.get_json()
    assert object == obj2
