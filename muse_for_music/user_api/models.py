"""Module containing models for whole API to use."""

from . import user_api as api
from ..hal_field import HaLUrl, UrlData, NestedFields

with_curies = api.model('WithCuries', {
    'curies': HaLUrl(UrlData('user_api.doc', absolute=True, templated=True,
                             hashtag='!{rel}', name='rel')),
})

root_links = api.inherit('RootLinks', with_curies, {
    'self': HaLUrl(UrlData('user_api.default_root_resource', absolute=True)),
    'login': HaLUrl(UrlData('user_api.auth_login', absolute=True)),
    'fresh_login': HaLUrl(UrlData('user_api.auth_fresh_login', absolute=True)),
    'refresh': HaLUrl(UrlData('user_api.auth_refresh', absolute=True)),
    'check': HaLUrl(UrlData('user_api.auth_check', absolute=True)),
})

root_model = api.model('RootModel', {
    '_links': NestedFields(root_links),
})
