from flask.testing import FlaskClient
from conftest import tempdir, app, auth, client, taxonomies
from hypothesis import given, strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule, initialize, precondition
from util import get_hateoas_resource, get_hateoas_ref, get_hateoas_ref_from_object, try_self_link, AuthActions, auth_header, PERSON_POST
from typing import Dict


class ApiChecker(RuleBasedStateMachine):

    api_rels = Bundle('rels')

    def __init__(self):
        super().__init__()
        self.tmp_context = tempdir()
        tmp = next(self.tmp_context)
        self.app_context = app(tmp)
        self.app = next(self.app_context)
        self.client = client(self.app)
        self.auth = auth(self.client)
        self.known_rels: Dict[str, Dict[str, str]] = {}
        self.auth_token = None

        # object state cache
        self.people_names = {'Unbekannt', }

    @initialize()
    def init_root(self):
        result = get_hateoas_resource(self.client)
        assert result.status_code == 200
        object = result.get_json()
        for rel in object['_links']:
            if rel == 'self' or rel == 'curies':
                continue
            self.known_rels[rel] = {'href': get_hateoas_ref_from_object(object, rel)}
            if rel == 'person':
                self.known_rels[rel]['POST'] = ['person']
        token = self.auth.login('admin', 'admin').get_json()['access_token']
        self.auth.add_role('user', auth=token)
        self.auth_token = self.auth.login('admin', 'admin').get_json()['access_token']

    def is_authenticated(self):
        return bool(self.auth_token)

    def can_post_person(self):
        return 'POST' in self.known_rels.get('person', {}) and self.is_authenticated()

    @precondition(lambda self: self.can_post_person())
    @rule(person=PERSON_POST)
    def add_person(self, person):
        url = get_hateoas_ref(self.client, *self.known_rels['person']['POST'], auth=self.auth_token)
        result = self.client.post(url, json=person, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}
        if result.status_code == 409:
            assert person['name'] in self.people_names
        else:
            self.people_names.add(person['name'])


muse_for_music_api_test = ApiChecker.TestCase

