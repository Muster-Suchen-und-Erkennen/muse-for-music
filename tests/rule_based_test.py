from collections import namedtuple
from random import choice
from flask.testing import FlaskClient
from conftest import tempdir, app, auth, client, taxonomies
from hypothesis import given, strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule, initialize, precondition, invariant, consumes, multiple
from util import get_hateoas_resource, get_hateoas_ref, get_hateoas_ref_from_object, try_self_link, compareObjects, AuthActions, auth_header
from util import ReferenceListPlaceholder, ReferencePlaceholder
from util import PERSON_POST, PERSON_PUT, OPUS_POST, OPUS_PUT, PART_POST, PART_PUT, SUB_PART_POST, SUB_PART_PUT, VOICE_POST, VOICE_PUT
from typing import Dict


ObjectReference = namedtuple('ObjectReference', ['type', 'id'])

PERSON_TYPE = 'person'
OPUS_TYPE = 'opus'
PART_TYPE = 'part'
SUBPART_TYPE = 'subpart'
VOICE_TYPE = 'voice'


class ApiChecker(RuleBasedStateMachine):

    # api_rels = Bundle('rels')
    persons = Bundle('persons')
    opera = Bundle('opera')
    parts = Bundle('parts')
    subparts = Bundle('subparts')
    voices = Bundle('voices')

    current_depth = -1
    DEPTH_TO_CHECK = -1

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
            PART_TYPE: set(),
            SUBPART_TYPE: set(),
            VOICE_TYPE: set(),
        }
        self.referenced_by_relations = {}
        self.reference_counter = {}
        self.consists_of_relations = {}
        self.people_names = set()
        self.opus_names = set()

        self.has_initialized_persons = False
        self.current_depth = -1

    def teardown(self):
        try:
            next(self.taxonomies_context, 0)
        except Exception as exc:
            pass
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

    def remove_from_bundle(self, ref: ObjectReference):
        bundle_name = None
        if ref.type == PERSON_TYPE:
            bundle_name = 'persons'
        elif ref.type == OPUS_TYPE:
            bundle_name = 'opera'
        elif ref.type == PART_TYPE:
            bundle_name = 'parts'
        elif ref.type == SUBPART_TYPE:
            bundle_name = 'subparts'
        elif ref.type == VOICE_TYPE:
            bundle_name = 'voices'
        else:
            assert False, 'Tried to delete a Object reference of an unknown type!'
        bundle = self.bundles.get(bundle_name, [])
        index_to_remove = None
        for i, name_ref in enumerate(bundle):
            value = self.names_to_values[name_ref.name]
            if value['id'] == ref.id:
                index_to_remove = i
                url = get_hateoas_ref_from_object(value, 'self')
                check_deleted_result = self.client.get(url, headers=auth_header(self.auth_token))
                assert check_deleted_result.status_code == 404, check_deleted_result.get_data().decode()
        assert index_to_remove is not None, 'The reference {} was not part of the bundle "{}" ({})!'.format(ref, bundle_name, bundle)
        bundle.pop(index_to_remove)

    def remove_reference(self, ref_to_delete: ObjectReference):
        for ref in self.referenced_by_relations[ref_to_delete]:
            # release reference counts
            self.reference_counter[ref] -= 1
        for ref in self.consists_of_relations[ref_to_delete]:
            # mark all (contained) objects as deleted
            self.remove_from_bundle(ref)
            self.remove_reference(ref)
        self.objects_by_type[ref_to_delete.type].remove(ref_to_delete)
        del self.consists_of_relations[ref_to_delete]
        del self.referenced_by_relations[ref_to_delete]
        del self.reference_counter[ref_to_delete]

    def can_test_person_count(self):
        return self.is_authenticated and self.has_initialized_persons

    @invariant()
    def reference_invariant(self):
        for ref, count in self.reference_counter.items():
            assert count >= 0, 'Invalid rference count for ref {}'.format(ref)

    @precondition(lambda self: self.can_test_person_count())
    @invariant()
    def person_count_invariant(self):
        all_people = get_hateoas_resource(self.client, 'person', auth=self.auth_token).get_json()
        assert len(all_people) == len(self.people_names)
        assert len(all_people) == len(self.objects_by_type[PERSON_TYPE])
        assert len(all_people) == len(self.bundles.get('persons', []))
        for person in all_people:
            assert person['name'] in self.people_names

    @precondition(lambda self: self.is_authenticated())
    @invariant()
    def opus_count_invariant(self):
        all_opera = get_hateoas_resource(self.client, 'opus', auth=self.auth_token).get_json()
        assert len(all_opera) == len(self.opus_names)
        assert len(all_opera) == len(self.objects_by_type[OPUS_TYPE])
        assert len(all_opera) == len(self.bundles.get('opera', []))
        for opus in all_opera:
            assert opus['name'] in self.opus_names

    @precondition(lambda self: self.is_authenticated())
    @invariant()
    def part_count_invariant(self):
        all_parts = get_hateoas_resource(self.client, 'part', auth=self.auth_token).get_json()
        assert len(all_parts) == len(self.objects_by_type[PART_TYPE])
        assert len(all_parts) == len(self.bundles.get('parts', []))


    ### Persons: ###############################################################

    def can_post_person(self):
        if self.DEPTH_TO_CHECK > 0 and self.current_depth > 0:
            return False
        return 'POST' in self.known_rels.get('person', {}) and self.is_authenticated() and len(self.objects_by_type[PERSON_TYPE]) < 10

    def can_put_person(self):
        if self.DEPTH_TO_CHECK > 0 and self.current_depth > 0:
            return False
        return self.is_authenticated() and self.objects_by_type[PERSON_TYPE]

    def can_delete_person(self):
        if self.DEPTH_TO_CHECK > 0 and self.current_depth > 0:
            return False
        return self.can_put_person()

    @initialize(target=persons)
    def init_person_unknown(self):
        self.login()
        result = get_hateoas_resource(self.client, 'person', 1, auth=self.auth_token)
        person = result.get_json()
        self.people_names.add(person['name'])
        ref = ObjectReference(PERSON_TYPE, person['id'])
        self.add_reference(ref)
        self.has_initialized_persons = True
        self.current_depth = max(self.current_depth, 0)
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
            self.current_depth = max(self.current_depth, 0)
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
            assert retry_result.status_code == 404, retry_result.get_data().decode()
            return multiple()

    ### Opera: #################################################################

    def can_post_opus(self):
        if self.DEPTH_TO_CHECK == 0:
            return False
        if self.DEPTH_TO_CHECK > 1 and self.current_depth > 1:
            return False
        can_post = 'POST' in self.known_rels.get('opus', {}) and self.is_authenticated()
        return can_post and bool(self.objects_by_type[PERSON_TYPE]) and len(self.objects_by_type[OPUS_TYPE]) < 10

    def can_put_opus(self):
        if self.DEPTH_TO_CHECK == 0:
            return False
        if self.DEPTH_TO_CHECK > 1 and self.current_depth > 1:
            return False
        can_put = self.is_authenticated() and bool(self.objects_by_type[PERSON_TYPE])
        return can_put and bool(self.objects_by_type[OPUS_TYPE])

    def can_delete_opus(self):
        if self.DEPTH_TO_CHECK == 0:
            return False
        if self.DEPTH_TO_CHECK > 1 and self.current_depth > 1:
            return False
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
            self.current_depth = max(self.current_depth, 1)
            return result.get_json()

    @precondition(lambda self: self.can_put_opus())
    @rule(target=opera, old_opus=consumes(opera), opus=OPUS_PUT, composer=persons)
    def update_opus(self, old_opus, opus, composer):
        url = get_hateoas_ref_from_object(old_opus, 'self')
        opus['id'] = old_opus['id']
        if opus['composer'].type == 'person':
            opus['composer'] = composer
        result = self.client.put(url, json=opus, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert opus['name'] in self.opus_names and opus['name'] != old_opus['name'], result.get_json()
            return old_opus
        else:
            assert opus['name'] not in self.opus_names or opus['name'] == old_opus['name']
            new_opus = result.get_json()
            try_self_link(new_opus, self.client, self.auth_token)
            compareObjects(old_opus, new_opus)
            if new_opus['name'] != old_opus['name']:
                self.opus_names.remove(old_opus['name'])
                self.opus_names.add(new_opus['name'])
            if new_opus['composer']['id'] != old_opus['composer']['id']:
                opus_ref = ObjectReference(OPUS_TYPE, old_opus['id'])
                old_composer_ref = ObjectReference(PERSON_TYPE, old_opus['composer']['id'])
                composer_ref = ObjectReference(PERSON_TYPE, new_opus['composer']['id'])
                self.remove_referenced_by_reference(opus_ref, old_composer_ref)
                self.add_referenced_by_reference(opus_ref, composer_ref)
            return new_opus

    @precondition(lambda self: self.can_delete_opus())
    @rule(target=opera, opus_to_delete=consumes(opera))
    def delete_opus(self, opus_to_delete):
        ref_to_delete = ObjectReference(OPUS_TYPE, opus_to_delete['id'])
        url = get_hateoas_ref_from_object(opus_to_delete, 'self')
        result = self.client.delete(url, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert self.reference_counter[ref_to_delete] > 0
            return opus_to_delete
        else:
            assert self.reference_counter[ref_to_delete] == 0
            self.remove_reference(ref_to_delete)
            self.opus_names.remove(opus_to_delete['name'])
            retry_result = self.client.get(url, headers=auth_header(self.auth_token))
            assert retry_result.status_code == 404, retry_result.get_data().decode()
            return multiple()

    ### Parts: #################################################################

    def can_post_part(self):
        if self.DEPTH_TO_CHECK == 0 or self.DEPTH_TO_CHECK == 1:
            return False
        if self.DEPTH_TO_CHECK > 2 and self.current_depth > 2:
            return False
        can_post = self.is_authenticated() and bool(self.objects_by_type[OPUS_TYPE])
        return can_post and len(self.objects_by_type[PART_TYPE]) < 50

    def can_put_part(self):
        if self.DEPTH_TO_CHECK == 0 or self.DEPTH_TO_CHECK == 1:
            return False
        if self.DEPTH_TO_CHECK > 2 and self.current_depth > 2:
            return False
        can_put = self.is_authenticated()
        return can_put and bool(self.objects_by_type[PART_TYPE])

    def can_delete_part(self):
        if self.DEPTH_TO_CHECK == 0 or self.DEPTH_TO_CHECK == 1:
            return False
        if self.DEPTH_TO_CHECK > 2 and self.current_depth > 2:
            return False
        return self.can_put_part()

    @precondition(lambda self: self.can_post_part())
    @rule(target=parts, part=PART_POST, opus=opera)
    def add_part(self, part, opus):
        url = get_hateoas_ref_from_object(opus, 'part')
        result = self.client.post(url, json=part, headers=auth_header(self.auth_token))
        assert result.status_code == 200, result.get_data().decode()
        new_part = result.get_json()
        try_self_link(new_part, self.client, self.auth_token)
        compareObjects(part, new_part)
        ref = ObjectReference(PART_TYPE, new_part['id'])
        self.add_reference(ref)
        opus_ref = ObjectReference(OPUS_TYPE, opus['id'])
        self.consists_of_relations[opus_ref].add(ref)
        self.current_depth = max(self.current_depth, 2)
        return result.get_json()

    @precondition(lambda self: self.can_put_part())
    @rule(target=parts, old_part=consumes(parts), part=PART_PUT)
    def update_part(self, old_part=None, part=None):
        url = get_hateoas_ref_from_object(old_part, 'self')
        part['id'] = old_part['id']
        result = self.client.put(url, json=part, headers=auth_header(self.auth_token))
        assert result.status_code == 200, result.get_data().decode()
        new_part = result.get_json()
        try_self_link(new_part, self.client, self.auth_token)
        compareObjects(old_part, new_part)
        return new_part

    @precondition(lambda self: self.can_delete_part())
    @rule(target=parts, part_to_delete=consumes(parts))
    def delete_part(self, part_to_delete):
        ref_to_delete = ObjectReference(PART_TYPE, part_to_delete['id'])
        url = get_hateoas_ref_from_object(part_to_delete, 'self')
        result = self.client.delete(url, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert self.reference_counter[ref_to_delete] > 0
            return part_to_delete
        else:
            assert self.reference_counter[ref_to_delete] == 0
            self.remove_reference(ref_to_delete)
            opus_ref = ObjectReference(OPUS_TYPE, part_to_delete['opus_id'])
            self.consists_of_relations[opus_ref].remove(ref_to_delete)
            retry_result = self.client.get(url, headers=auth_header(self.auth_token))
            assert retry_result.status_code == 404, retry_result.get_data().decode()
            return multiple()

    ### SubParts: ##############################################################

    def can_post_sub_part(self):
        if self.DEPTH_TO_CHECK >= 0 or self.DEPTH_TO_CHECK <= 2:
            return False
        if self.DEPTH_TO_CHECK > 3 and self.current_depth > 3:
            return False
        can_post = self.is_authenticated() and bool(self.objects_by_type[PART_TYPE])
        return can_post and len(self.objects_by_type[SUBPART_TYPE]) < 50

    def can_put_sub_part(self):
        if self.DEPTH_TO_CHECK >= 0 or self.DEPTH_TO_CHECK <= 2:
            return False
        if self.DEPTH_TO_CHECK > 3 and self.current_depth > 3:
            return False
        can_put = self.is_authenticated()
        return can_put and bool(self.objects_by_type[SUBPART_TYPE])

    def can_delete_sub_part(self):
        if self.DEPTH_TO_CHECK >= 0 or self.DEPTH_TO_CHECK <= 2:
            return False
        if self.DEPTH_TO_CHECK > 3 and self.current_depth > 3:
            return False
        return self.can_put_sub_part()

    @precondition(lambda self: self.can_post_sub_part())
    @rule(target=subparts, subpart=SUB_PART_POST, part=parts)
    def add_subpart(self, subpart, part):
        url = get_hateoas_ref_from_object(part, 'subpart')
        result = self.client.post(url, json=subpart, headers=auth_header(self.auth_token))
        assert result.status_code == 200, result.get_data().decode()
        new_subpart = result.get_json()
        try_self_link(new_subpart, self.client, self.auth_token)
        compareObjects(subpart, new_subpart)
        ref = ObjectReference(SUBPART_TYPE, new_subpart['id'])
        self.add_reference(ref)
        part_ref = ObjectReference(PART_TYPE, part['id'])
        self.consists_of_relations[part_ref].add(ref)
        self.current_depth = max(self.current_depth, 3)
        return result.get_json()

    @precondition(lambda self: self.can_put_sub_part())
    @rule(target=subparts, old_sub_part=consumes(subparts), sub_part=SUB_PART_PUT)
    def update_sub_part(self, old_sub_part=None, sub_part=None):
        url = get_hateoas_ref_from_object(old_sub_part, 'self')
        sub_part['id'] = old_sub_part['id']
        result = self.client.put(url, json=sub_part, headers=auth_header(self.auth_token))
        assert result.status_code == 200, result.get_data().decode()
        new_sub_part = result.get_json()
        try_self_link(new_sub_part, self.client, self.auth_token)
        compareObjects(old_sub_part, new_sub_part)
        return new_sub_part

    @precondition(lambda self: self.can_delete_sub_part())
    @rule(target=subparts, sub_part_to_delete=consumes(subparts))
    def delete_sub_part(self, sub_part_to_delete):
        ref_to_delete = ObjectReference(SUBPART_TYPE, sub_part_to_delete['id'])
        url = get_hateoas_ref_from_object(sub_part_to_delete, 'self')
        result = self.client.delete(url, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert self.reference_counter[ref_to_delete] > 0
            return sub_part_to_delete
        else:
            assert self.reference_counter[ref_to_delete] == 0
            self.remove_reference(ref_to_delete)
            part_ref = ObjectReference(PART_TYPE, sub_part_to_delete['part_id'])
            self.consists_of_relations[part_ref].remove(ref_to_delete)
            retry_result = self.client.get(url, headers=auth_header(self.auth_token))
            assert retry_result.status_code == 404, retry_result.get_data().decode()
            return multiple()

    ### Voices: ################################################################

    def can_post_voice(self):
        if self.DEPTH_TO_CHECK >= 0 or self.DEPTH_TO_CHECK <= 3:
            return False
        can_post = self.is_authenticated() and bool(self.objects_by_type[SUBPART_TYPE])
        return can_post and len(self.objects_by_type[VOICE_TYPE]) < 100

    def can_put_voice(self):
        if self.DEPTH_TO_CHECK >= 0 or self.DEPTH_TO_CHECK <= 3:
            return False
        can_put = self.is_authenticated()
        return can_put and bool(self.objects_by_type[VOICE_TYPE])

    def can_delete_voice(self):
        if self.DEPTH_TO_CHECK >= 0 or self.DEPTH_TO_CHECK <= 3:
            return False
        return self.can_put_voice()

    @precondition(lambda self: self.can_post_voice())
    @rule(target=voices, voice=VOICE_POST, subpart=subparts)
    def add_voice(self, voice, subpart):
        url = get_hateoas_ref_from_object(subpart, 'voice')
        result = self.client.post(url, json=voice, headers=auth_header(self.auth_token))
        assert result.status_code == 200, result.get_data().decode()
        new_voice = result.get_json()
        try_self_link(new_voice, self.client, self.auth_token)
        compareObjects(voice, new_voice)
        ref = ObjectReference(VOICE_TYPE, new_voice['id'])
        self.add_reference(ref)
        subpart_ref = ObjectReference(SUBPART_TYPE, subpart['id'])
        self.consists_of_relations[subpart_ref].add(ref)
        self.current_depth = max(self.current_depth, 4)
        return result.get_json()

    @precondition(lambda self: self.can_put_voice())
    @rule(target=voices, old_voice=consumes(voices), voice=VOICE_PUT, cited_composers=st.lists(persons, unique_by=lambda p: p['id']), data=st.data())
    def update_voice(self, old_voice=None, voice=None, cited_composers=[], data=None):
        url = get_hateoas_ref_from_object(old_voice, 'self')
        voice['id'] = old_voice['id']
        # remove related voices for now
        voice['related_voices'] = []
        # handle citations
        if isinstance(voice['citations']['composer_citations'], ReferenceListPlaceholder):
            voice['citations']['composer_citations'] = cited_composers
        for citation in voice['citations']['opus_citations']:
            citation['opus'] = data.draw(self.opera)
        result = self.client.put(url, json=voice, headers=auth_header(self.auth_token))
        assert result.status_code == 200, result.get_data().decode()
        new_voice = result.get_json()
        try_self_link(new_voice, self.client, self.auth_token)
        compareObjects(old_voice, new_voice)

        # handle references:
        ref = ObjectReference(VOICE_TYPE, new_voice['id'])

        # composer citation references
        old_composer_citations = set([ObjectReference(PERSON_TYPE, p['id']) for p in old_voice['citations']['composer_citations']])
        new_composer_citations = set([ObjectReference(PERSON_TYPE, p['id']) for p in voice['citations']['composer_citations']])
        for old_citation_ref in old_composer_citations - new_composer_citations:
            self.remove_referenced_by_reference(ref, old_citation_ref)
        for new_citation_ref in new_composer_citations - old_composer_citations:
            self.add_referenced_by_reference(ref, new_citation_ref)

        # opus citation references
        old_opus_citations = set([
            ObjectReference(OPUS_TYPE, c['opus']['id']) for c in old_voice['citations']['opus_citations']
        ])
        new_opus_citations = set([
            ObjectReference(OPUS_TYPE, c['opus']['id']) for c in voice['citations']['opus_citations']
        ])
        for old_citation_ref in old_opus_citations - new_opus_citations:
            self.add_referenced_by_reference(ref, old_citation_ref)
        for new_citation_ref in new_opus_citations - old_opus_citations:
            self.add_referenced_by_reference(ref, new_citation_ref)
        return new_voice


    @precondition(lambda self: self.can_delete_voice())
    @rule(target=voices, voice_to_delete=consumes(voices))
    def delete_voice(self, voice_to_delete):
        ref_to_delete = ObjectReference(VOICE_TYPE, voice_to_delete['id'])
        url = get_hateoas_ref_from_object(voice_to_delete, 'self')
        result = self.client.delete(url, headers=auth_header(self.auth_token))
        assert result.status_code in {200, 409}, result.get_data().decode()
        if result.status_code == 409:
            assert self.reference_counter[ref_to_delete] > 0
            return voice_to_delete
        else:
            assert self.reference_counter[ref_to_delete] == 0
            self.remove_reference(ref_to_delete)
            subpart_ref = ObjectReference(SUBPART_TYPE, voice_to_delete['subpart_id'])
            self.consists_of_relations[subpart_ref].remove(ref_to_delete)
            retry_result = self.client.get(url, headers=auth_header(self.auth_token))
            assert retry_result.status_code == 404, retry_result.get_data().decode()
            return multiple()


test_muse_for_music_api = ApiChecker.TestCase


@given(data=st.data())
def test_debug_test(app, taxonomies, data):
    """Test case to debug hypothesis strategies with."""
    with app.app_context():
        value = data.draw(VOICE_PUT)
        assert value is not None
        print(value)

