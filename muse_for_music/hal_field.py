from collections import OrderedDict
from functools import wraps
from flask_restx import marshal
from flask_restx.fields import Raw, Nested, StringMixin, MarshallingError, get_value, urlparse, urlunparse
from typing import Dict, List, Union
from flask import url_for, request, current_app

# monkeypatch flask restplus to allow custom fields
if True:
    old_init = Raw.__init__
    @wraps(old_init)
    def newInit(self, **kwargs):
        old_init(self, **kwargs)
        std_args = ('default', 'attribute', 'title', 'description', 'required', 'readonly', 'example', 'mask')
        self.extra_attributes = {'x-'+k: v for k, v in kwargs.items() if k not in std_args}
    Raw.__init__ = newInit

    old_schema = Raw.schema
    @wraps(old_schema)
    def newSchema(self):
        schema = old_schema(self)
        for k, v in self.extra_attributes.items():
            schema[k] = v
        return schema
    Raw.schema = newSchema

    from flask_restx.model import Model, iteritems, instance, not_none

    def _schema(self):
        properties = OrderedDict()
        required = set()
        discriminator = None
        for i, (name, field) in enumerate(iteritems(self)):
            field = instance(field)
            properties[name] = field.__schema__
            properties[name]['x-order'] = i + 1
            if field.required:
                required.add(name)
            if getattr(field, 'discriminator', False):
                discriminator = name

        return not_none({
            'required': sorted(list(required)) or None,
            'properties': properties,
            'discriminator': discriminator,
            'x-mask': str(self.__mask__) if self.__mask__ else None,
            'type': 'object',
        })

    setattr(Model, '_schema', property(_schema))


class NestedFields(Nested):

    def __init__(self, model, **kwargs):
        super().__init__(model=model, **kwargs)

    def output(self, key, obj, ordered=False):
        return marshal(obj, self.nested)


class NestedModel():

    def __init__(self, model, attribute: str=None, as_list: bool=False):
        self.model = model
        self.attribute = attribute
        self.as_list = as_list

    @property
    def nested(self):
        return getattr(self.model, 'resolved', self.model)


class EmbeddedFields(Raw):

    def __init__(self, embedded_models: Dict[str, NestedModel], **kwargs):
        self.embedded_models = embedded_models
        super().__init__(**kwargs)

    def nested_model(self, name):
        return self.embedded_models[name].nested

    def output(self, key, obj, orderes=False):
        data = {}

        for name in self.embedded_models:
            key = name if not self.embedded_models[name].attribute else self.embedded_models[name].attribute
            value = get_value(key, obj)
            if value is not None and not (self.embedded_models[name].as_list and (len(value) == 0)):
                data[name] = marshal(value, self.nested_model(name))
        return data

    def schema(self):
        schema = super().schema()
        schema['type'] = 'object'
        schema['required'] = list(self.embedded_models.keys())
        props = OrderedDict()

        for name in self.embedded_models:
            ref = '#/definitions/{0}'.format(self.nested_model(name).name)
            if not self.embedded_models[name].as_list:
                props[name] = {'$ref': ref}
            else:
                props[name] = {'type': 'array', 'items': {'$ref': ref}}
        schema['properties'] = props

        return schema


class UrlData():

    def __init__(self, endpoint: str, absolute=False, scheme=None, url: str=None,
                 title: str=None, name: str=None, templated: bool=False, url_data: dict={},
                 path_variables: list=[], hashtag: str=None, force_trailing_slash: bool=True):
        self.endpoint = endpoint
        self.absolute = absolute
        self.scheme = scheme
        self._url = url
        self.title = title
        self.name = name
        self.templated = bool(templated)
        self.url_data = url_data
        self.path_variables = ''
        if path_variables:
            self.path_variables = '/'.join('{{{}}}'.format(var) for var in path_variables)
        self.hashtag = ''
        if hashtag is not None:
            self.hashtag = hashtag
        self.force_trailing_slash = force_trailing_slash

    def url(self, obj):
        if self._url:
            return self._url
        url_data = {}
        for key in self.url_data:
            value = get_value(self.url_data[key], obj)
            if value is None:
                current_app.logger.debug('Could not build url because some provided values were none.\n' +
                                 'UrlParam: "%s", ObjectKey: "%s"',
                                 key, self.url_data[key])
                from flask import request
                print(request)
                print(obj)
                return None
            url_data[key] = value
        endpoint = self.endpoint if self.endpoint is not None else request.endpoint
        o = urlparse(url_for(endpoint, _external=self.absolute, **url_data))
        path = ''
        if o.path.endswith('/') or not self.force_trailing_slash:
            path = o.path + self.path_variables
        else:
            path = o.path + '/' + self.path_variables
        if self.absolute:
            scheme = self.scheme if self.scheme is not None else o.scheme
            return urlunparse((scheme, o.netloc, path, "", "", self.hashtag))
        else:
            return urlunparse(("", "", path, "", "", self.hashtag))


class HaLUrl(StringMixin, Raw):
    '''
    A string representation of a Url

    :param str endpoint: Endpoint name. If endpoint is ``None``, ``request.endpoint`` is used instead
    :param bool absolute: If ``True``, ensures that the generated urls will have the hostname included
    :param str scheme: URL scheme specifier (e.g. ``http``, ``https``)
    '''
    __schema_type__ = 'link'

    def __init__(self, url_data: Union[UrlData, List[UrlData]], **kwargs):
        super().__init__(readonly=True, **kwargs)
        self.url_data = url_data
        self.is_list = isinstance(url_data, list)

    def output(self, key, obj, ordered=False):
        output = {}
        if self.is_list:
            output = []
            for data in UrlData:
                output.append(self.generate_link(data, obj))
        else:
            output = self.generate_link(self.url_data, obj)

        return output

    def generate_link(self, url_data: UrlData, obj):
        link = OrderedDict()
        link['templated'] = url_data.templated
        if url_data.title:
            link['title'] = str(url_data.title)
        if url_data.name:
            link['name'] = str(url_data.name)
        try:
            link['href'] = url_data.url(obj)
        except TypeError as te:
            raise MarshallingError(te)
        return link

    def schema(self):
        schema = super().schema()

        link_schema = schema

        if self.is_list:
            link_schema = {}
            schema['type'] = 'array'
            schema['items'] = link_schema

        link_schema['type'] = 'object'
        link_schema['required'] = ['href']
        props = OrderedDict()
        props['href'] = {'type': 'string', 'readOnly': True, 'example': 'http://www.example.com/api'}
        props['templated'] = {'type': 'boolean', 'readOnly': True}
        props['title'] = {'type': 'string', 'readOnly': True}
        props['name'] = {'type': 'string', 'readOnly': True}
        link_schema['properties'] = props

        return schema
