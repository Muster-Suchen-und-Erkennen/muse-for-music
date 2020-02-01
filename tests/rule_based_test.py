from collections import namedtuple
from random import choice
from flask.testing import FlaskClient
from conftest import tempdir, app, auth, client, taxonomies
from hypothesis import given, strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule, initialize, precondition, invariant, consumes, multiple
from util import get_hateoas_resource, get_hateoas_ref, get_hateoas_ref_from_object, try_self_link, compareObjects, AuthActions, auth_header
from util import PERSON_POST, PERSON_PUT, OPUS_POST, OPUS_PUT
from typing import Dict


ObjectReference = namedtuple('ObjectReference', ['type', 'id'])

PERSON_TYPE = 'person'
OPUS_TYPE = 'opus'


class ApiChecker(RuleBasedStateMachine):

    # api_rels = Bundle('rels')
    persons = Bundle('persons')
    opera = Bundle('opera')

    def __init__(self):
        super().__init__()
        self.app_context = app()
        self.app = next(self.app_context)
        self.taxonomies_context = taxonomies(self.app)
        self.taxonomies = next(self.taxonomies_context)
        self.client = client(self.app)
        self.auth = auth(self.client)
        self.known_rels: Dict[str, Dict[str, str]] = {}
        self.auth_token = None

        # object state cache
        self.objects_by_type = {
            PERSON_TYPE: set(),
            OPUS_TYPE: set(),
        }
        self.referenced_by_relations = {}
        self.reference_counter = {}
        self.consists_of_relations = {}
        self.people_names = {'Unbekannt', }
        self.opus_names = set()

    def teardown(self):
        try:
            next(self.taxonomies_context, 0)
        except Exception as exc:
            print(exc)
        try:
            next(self.app_context, 0)
        except Exception:
            pass

    def login(self):
        if self.auth_token is None:
            token = self.auth.login('admin', 'admin').get_json()['access_token']
            self.auth.add_role('user', auth=token)
            self.auth_token = self.auth.login('admin', 'admin').get_json()['access_token']

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
            elif rel == 'opus':
                self.known_rels[rel]['POST'] = ['opus']
        self.login()

    def is_authenticated(self):
        return bool(self.auth_token)

    def add_reference(self, ref: ObjectReference):
        self.referenced_by_relations[ref] = set()
        self.consists_of_relations[ref] = set()
        self.objects_by_type[ref.type].add(ref)
        self.reference_counter[ref] = 0

    def add_referenced_by_reference(self, ref: ObjectReference, referenced_object: ObjectReference):
        self.referenced_by_relations[ref].add(referenced_object)
        self.reference_counter[referenced_object] += 1

    def remove_referenced_by_reference(self, ref: ObjectReference, referenced_object: ObjectReference):
        self.referenced_by_relations[ref].remove(referenced_object)
        self.reference_counter[referenced_object] -= 1

    def remove_reference(self, ref_to_delete: ObjectReference):
        self.objects_by_type[ref_to_delete.type].remove(ref_to_delete)
        del self.consists_of_relations[ref_to_delete]
        del self.referenced_by_relations[ref_to_delete]
        del self.reference_counter[ref_to_delete]

    @invariant()
    @rule()
    def reference_invariant(self):
        for ref, count in self.reference_counter.items():
            assert count >= 0, 'Invalid rference count for ref {}'.format(ref)

    ### Persons: ###############################################################

    def can_post_person(self):
        return 'POST' in self.known_rels.get('person', {}) and self.is_authenticated()

    def can_put_person(self):
        return self.can_post_person() and self.objects_by_type[PERSON_TYPE]

    def can_delete_person(self):
        return self.can_put_person()

    @initialize(target=persons)
    def init_person_unknown(self):
        self.login()
        result = get_hateoas_resource(self.client, 'person', 1, auth=self.auth_token)
        person = result.get_json()
        self.people_names.add(person['name'])
        ref = ObjectReference(PERSON_TYPE, person['id'])
        self.add_reference(ref)
        return person

    @precondition(lambda self: self.can_post_person())
    @rule(target=persons, person=PERSON_POST)
    def add_person(self, person):
        url = get_hateoas_ref(self.client, *self.known_rels['person']['POST'], auth=self.auth_token)
        result = self.client.post(url, json=person, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert person['name'] in self.people_names
            return multiple()
        else:
            assert person['name'] not in self.people_names
            new_person = result.get_json()
            try_self_link(new_person, self.client, self.auth_token)
            compareObjects(person, new_person)
            self.people_names.add(person['name'])
            ref = ObjectReference(PERSON_TYPE, new_person['id'])
            self.add_reference(ref)
            return new_person

    @precondition(lambda self: self.can_put_person())
    @rule(target=persons, old_person=consumes(persons), person=PERSON_PUT)
    def update_person(self, old_person, person):
        url = get_hateoas_ref_from_object(old_person, 'self')
        person['id'] = old_person['id']
        result = self.client.put(url, json=person, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert person['name'] in self.people_names and person['name'] != old_person['name']
            return old_person
        else:
            assert person['name'] not in self.people_names or person['name'] == old_person['name']
            new_person = result.get_json()
            try_self_link(new_person, self.client, self.auth_token)
            compareObjects(old_person, new_person)
            if person['name'] != old_person['name']:
                self.people_names.remove(old_person['name'])
                self.people_names.add(person['name'])
            return new_person

    @precondition(lambda self: self.can_delete_person())
    @rule(target=persons, person_to_delete=consumes(persons))
    def delete_person(self, person_to_delete):
        ref_to_delete = ObjectReference(PERSON_TYPE, person_to_delete['id'])
        url = get_hateoas_ref_from_object(person_to_delete, 'self')
        result = self.client.delete(url, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert self.reference_counter[ref_to_delete] > 0
            return person_to_delete
        else:
            assert self.reference_counter[ref_to_delete] == 0
            self.remove_reference(ref_to_delete)
            self.people_names.remove(person_to_delete['name'])
            retry_result = self.client.get(url, headers=auth_header(self.auth_token))
            assert retry_result.status_code == 404, result.get_data().decode()
            return multiple()

    ### Opera: #################################################################

    def can_post_opus(self):
        can_post = 'POST' in self.known_rels.get('opus', {}) and self.is_authenticated()
        return can_post and bool(self.objects_by_type[PERSON_TYPE])

    def can_put_opus(self):
        return self.can_post_opus() and bool(self.objects_by_type[OPUS_TYPE])

    def can_delete_opus(self):
        return self.can_put_opus()

    @precondition(lambda self: self.can_post_opus())
    @rule(target=opera, opus=OPUS_POST, composer=persons)
    def add_opus(self, opus, composer):
        url = get_hateoas_ref(self.client, *self.known_rels['opus']['POST'], auth=self.auth_token)
        if opus['composer'].type == 'person':
            opus['composer'] = composer
        result = self.client.post(url, json=opus, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert opus['name'] in self.opus_names, result
            return multiple()
        else:
            assert opus['name'] not in self.opus_names
            new_opus = result.get_json()
            try_self_link(new_opus, self.client, self.auth_token)
            compareObjects(opus, new_opus)
            self.opus_names.add(opus['name'])
            ref = ObjectReference(OPUS_TYPE, new_opus['id'])
            self.add_reference(ref)
            self.add_referenced_by_reference(ref, ObjectReference(PERSON_TYPE, composer['id']))
            return result.get_json()


muse_for_music_api_test = ApiChecker.TestCase

