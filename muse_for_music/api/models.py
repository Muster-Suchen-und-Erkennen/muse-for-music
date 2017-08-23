
from . import api
from ..hal_field import HaLUrl, UrlData, NestedFields

with_curies = api.model('WithCuries', {
    'curies': HaLUrl(UrlData('api.doc', absolute=True, templated=True,
                             hashtag='!{rel}', name='rel')),
})

root_links = api.inherit('RootLinks', with_curies, {
    'self': HaLUrl(UrlData('api.default_root_resource', absolute=True)),
    'rel:taxonomy': HaLUrl(UrlData('api.taxonomies_taxonomy_list_resource', absolute=True)),
    'rel:data': HaLUrl(UrlData('api.data_data_resource', absolute=True)),
})

root_model = api.model('RootModel', {
    '_links': NestedFields(root_links),
})
