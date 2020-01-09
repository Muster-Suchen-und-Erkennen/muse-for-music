from collections import namedtuple
from random import choice
from flask.testing import FlaskClient
from conftest import tempdir, app, auth, client, taxonomies
from hypothesis import given, strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule, initialize, precondition
from util import get_hateoas_resource, get_hateoas_ref, get_hateoas_ref_from_object, try_self_link, compareObjects, AuthActions, auth_header
from util import PERSON_POST, PERSON_PUT, OPUS_POST, OPUS_PUT
from typing import Dict


ObjectReference = namedtuple('ObjectReference', ['type', 'id'])

PERSON_TYPE = 'person'


class ApiChecker(RuleBasedStateMachine):

    #api_rels = Bundle('rels')

    def __init__(self):
        super().__init__()
        self.app_context = app()
        self.app = next(self.app_context)
        self.client = client(self.app)
        self.auth = auth(self.client)
        self.known_rels: Dict[str, Dict[str, str]] = {}
        self.auth_token = None

        # object state cache
        self.objects_by_type = {
            PERSON_TYPE: [ObjectReference(PERSON_TYPE, 1)],
        }
        self.referenced_by_relations = {ObjectReference(PERSON_TYPE, 1): set()}
        self.consists_of_relations = {}
        self.people_names = {'Unbekannt', }

    def teardown(self):
        next(self.app_context, 0)

    @initialize()
    def init_root(self):
        result = get_hateoas_resource(self.client)
        assert result.status_code == 200, result.get_data().decode()
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

    def can_put_person(self):
        return self.can_post_person() and self.objects_by_type[PERSON_TYPE]

    def can_delete_person(self):
        return self.can_put_person()

    @precondition(lambda self: self.can_post_person())
    @rule(person=PERSON_POST)
    def add_person(self, person):
        url = get_hateoas_ref(self.client, *self.known_rels['person']['POST'], auth=self.auth_token)
        result = self.client.post(url, json=person, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert person['name'] in self.people_names
        else:
            assert person['name'] not in self.people_names
            new_person = result.get_json()
            try_self_link(new_person, self.client, self.auth_token)
            compareObjects(person, new_person)
            self.people_names.add(person['name'])
            ref = ObjectReference(PERSON_TYPE, new_person['id'])
            self.referenced_by_relations[ref] = set()
            self.consists_of_relations[ref] = set()
            self.objects_by_type[PERSON_TYPE].append(ref)

    @precondition(lambda self: self.can_put_person())
    @rule(person=PERSON_PUT)
    def update_person(self, person):
        ref_to_update = choice(self.objects_by_type[PERSON_TYPE])
        old_person = get_hateoas_resource(self.client, 'person', ref_to_update.id, auth=self.auth_token).get_json()
        url = get_hateoas_ref_from_object(old_person, 'self')
        person['id'] = old_person['id']
        result = self.client.put(url, json=person, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert person['name'] in self.people_names and person['name'] != old_person['name']
        else:
            assert person['name'] not in self.people_names or person['name'] == old_person['name']
            new_person = result.get_json()
            try_self_link(new_person, self.client, self.auth_token)
            compareObjects(old_person, new_person)
            if person['name'] != old_person['name']:
                self.people_names.remove(old_person['name'])
                self.people_names.add(person['name'])

    @precondition(lambda self: self.can_delete_person())
    def delete_person(self):
        ref_to_delete = choice(self.objects_by_type[PERSON_TYPE])
        old_person = get_hateoas_resource(self.client, 'person', ref_to_update.id, auth=self.auth_token).get_json()
        url = get_hateoas_ref_from_object(old_person, 'self')
        result = self.client.delete(url, headers=auth_header(self.auth_token))
        assert result.status_code == 200, result.get_data().decode()
        self.objects_by_type[PERSON_TYPE].remove(ref_to_delete)
        del self.consists_of_relations[ref_to_delete]
        del self.referenced_by_relations[ref_to_delete]
        self.people_names.remove(old_person['name'])
        retry_result = self.client.get(url, headers=auth_header(self.auth_token))
        assert retry_result.status_code == 404, result.get_data().decode()


muse_for_music_api_test = ApiChecker.TestCase

