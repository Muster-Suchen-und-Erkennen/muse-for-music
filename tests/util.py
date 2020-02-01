from collections import namedtuple
from hypothesis import assume, reject, strategies as st
from flask_restplus import fields, Model

from muse_for_music.api import api
from muse_for_music.models.taxonomies import get_taxonomies


ReferencePlaceholder = namedtuple('ReferencePlaceholder', ['type', 'nullable'])


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


def taxonomy_strategy(taxonomy: str, nullable: bool=False):
    choices = []
    if nullable:
        choices.append({
            'id': -1,
            'name': 'null',
            'description': 'null',
        })
    taxonomies = get_taxonomies()
    tax = taxonomies[taxonomy.upper()]
    items = tax.query.all()
    for item in items:
        choices.append({
            'id': item.id,
            'name': item.name,
            'description': item.description,
        })
    return st.sampled_from(choices)


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
        if 'x-reference' in field.extra_attributes:
            reference_type = field.extra_attributes['x-reference']
            nullable = field.extra_attributes.get('x-nullable', False)
            return st.just(ReferencePlaceholder(reference_type, nullable))
        elif 'x-taxonomy' in field.extra_attributes:
            taxonomy = field.extra_attributes['x-taxonomy']
            nullable = field.extra_attributes.get('x-nullable', False)
            return st.deferred(lambda: taxonomy_strategy(taxonomy, nullable))
        return(st.deferred(lambda: dict_model_example(field.model)))
    return field_default_strategy(field)


def field_default_strategy(field: fields.Raw):
    try:
        if field.default is not None:
            if isinstance(field, fields.String):
                if field.min_length is not None and len(field.default) < field.min_length:
                    return field_strategy(field)
                if field.max_length is not None and len(field.default) > field.max_length:
                    return field_strategy(field)
            return st.just(field.default)
    except AttributeError:
        pass
    if isinstance(field, fields.Nested):
        if 'x-reference' in field.extra_attributes:
            reference_type = field.extra_attributes['x-reference']
            nullable = field.extra_attributes.get('x-nullable', False)
            return st.just(ReferencePlaceholder(reference_type, nullable))
        elif 'x-taxonomy' in field.extra_attributes:
            taxonomy = field.extra_attributes['x-taxonomy']
            nullable = field.extra_attributes.get('x-nullable', False)
            return st.deferred(lambda: taxonomy_strategy(taxonomy, nullable))
        return(st.deferred(lambda: dict_model_default(field.model)))
    return field_strategy(field)


def field_strategy(field: fields.Raw):
    try:
        if field.enum is not None:
            return st.sampled_from(field.enum)
    except AttributeError:
        pass
    if isinstance(field, fields.String):
        min_size = 0 if field.min_length is None else field.min_length
        max_size = 500 if field.max_length is None else field.max_length
        return st.text(min_size=min_size, max_size=max_size)
    elif isinstance(field, fields.Integer):
        minimum = -(2 ** 31) if field.minimum is None else field.minimum
        maximum = (2 ** 31) - 1 if field.maximum is None else field.maximum
        return st.integers(min_value=minimum, max_value=maximum)
    elif isinstance(field, fields.Nested):
        if 'x-reference' in field.extra_attributes:
            reference_type = field.extra_attributes['x-reference']
            nullable = field.extra_attributes.get('x-nullable', False)
            return st.just(ReferencePlaceholder(reference_type, nullable))
        elif 'x-taxonomy' in field.extra_attributes:
            taxonomy = field.extra_attributes['x-taxonomy']
            nullable = field.extra_attributes.get('x-nullable', False)
            return st.deferred(lambda: taxonomy_strategy(taxonomy, nullable))
        return st.deferred(lambda: dict_model_strategy(field.model))
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
        if isinstance(rel, int):
            url = url + '{}/'.format(rel)
            continue
        result = client.get(url, headers=headers)
        url = result.get_json()['_links'][rel]['href']
    return url


def get_hateoas_resource(client, *rels, auth=None, root='api'):
    headers = auth_header(auth)
    url = get_hateoas_ref(client, *rels, auth=auth, root=root)
    return client.get(url, headers=headers)


def try_self_link(object, client, auth=None):
    headers = auth_header(auth)
    url = object['_links']['self']['href']
    result = client.get(url, headers=headers)
    assert result.status_code == 200, result.get_data().decode()
    obj2 = result.get_json()
    assert object == obj2


def compareObjects(a, b):
    if isinstance(a, dict):
        if not isinstance(b, dict):
            return False
        for key, value in a.items():
            return compareObjects(value, b[key])
    elif isinstance(a, (list, tuple)):
        if not isinstance(b, (list, tuple)):
            return False
        if len(a) != len(b):
            return False
        for val_a, val_b in zip(a, b):
            if not compareObjects(val_a, val_b):
                return False
        return True
    return a == b
