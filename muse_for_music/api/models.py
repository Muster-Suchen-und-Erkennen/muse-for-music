"""Module containing models for whole API to use."""

from . import api
from ..hal_field import HaLUrl, UrlData, NestedFields

with_curies = api.model('WithCuries', {
    'curies': HaLUrl(UrlData('api.doc', absolute=True, templated=True,
                             hashtag='!{rel}', name='rel')),
})

root_links = api.inherit('RootLinks', with_curies, {
    'self': HaLUrl(UrlData('api.default_root_resource', absolute=True)),
    'doc': HaLUrl(UrlData('api.doc', absolute=True)),
    'spec': HaLUrl(UrlData('api.specs', absolute=True, force_trailing_slash=False)),
    'taxonomy': HaLUrl(UrlData('api.taxonomies_taxonomy_list_resource', absolute=True)),
    'person': HaLUrl(UrlData('api.person_person_list_resource', absolute=True)),
    'opus': HaLUrl(UrlData('api.opus_opus_list_resource', absolute=True)),
    'part': HaLUrl(UrlData('api.part_parts_list_resource', absolute=True)),
    'subpart': HaLUrl(UrlData('api.subpart_sub_part_list_resource', absolute=True)),
    'history': HaLUrl(UrlData('api.history_history_resource', absolute=True)),
})

root_model = api.model('RootModel', {
    '_links': NestedFields(root_links),
})
