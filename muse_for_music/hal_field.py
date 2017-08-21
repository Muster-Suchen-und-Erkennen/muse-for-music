from collections import OrderedDict
from flask_restplus import marshal
from flask_restplus.fields import Raw, Nested, StringMixin, MarshallingError, get_value, urlparse, urlunparse
from flask import url_for, request
from typing import Dict


class NestedFields(Nested):

    def __init__(self, model, **kwargs):
        super().__init__(model=model, **kwargs)

    def output(self, key, obj):

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

    def output(self, key, obj):
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

        print(schema)

        return schema


class HaLUrl(StringMixin, Raw):
    '''
    A string representation of a Url

    :param str endpoint: Endpoint name. If endpoint is ``None``, ``request.endpoint`` is used instead
    :param bool absolute: If ``True``, ensures that the generated urls will have the hostname included
    :param str scheme: URL scheme specifier (e.g. ``http``, ``https``)
    '''
    __schema_type__ = 'link'

    def __init__(self, endpoint=None, absolute=False, scheme=None, title: str=None,
                 templated: bool=False, data: dict={}, path_variables: list=[], **kwargs):
        super().__init__(readonly=True, **kwargs)
        self.endpoint = endpoint
        self.absolute = absolute
        self.scheme = scheme
        self.title = title
        self.templated = bool(templated)
        self.data = data
        self.path_variables = ''
        if path_variables:
            self.path_variables = '/'.join('{{?{}}}'.format(var) for var in path_variables)

    def output(self, key, obj):
        link = OrderedDict()
        link['templated'] = self.templated
        if self.title:
            link['title'] = str(self.title)
        try:
            data = {}
            for key in self.data:
                value = get_value(self.data[key], obj)
                if value is None:
                    return None
                data[key] = value
            endpoint = self.endpoint if self.endpoint is not None else request.endpoint
            o = urlparse(url_for(endpoint, _external=self.absolute, **data))
            path = ''
            if o.path.endswith('/'):
                path = o.path + self.path_variables
            else:
                path = o.path + '/' + self.path_variables
            if self.absolute:
                scheme = self.scheme if self.scheme is not None else o.scheme
                link['href'] = urlunparse((scheme, o.netloc, path, "", "", ""))
            else:
                link['href'] = urlunparse(("", "", path, "", "", ""))
        except TypeError as te:
            raise MarshallingError(te)
        return link

    def schema(self):
        schema = super().schema()

        schema['type'] = 'object'
        schema['required'] = ['href']
        props = OrderedDict()
        props['href'] = {'type': 'string', 'readOnly': True, 'example': 'http://www.example.com/api'}
        props['templated'] = {'type': 'boolean', 'readOnly': True}
        props['title'] = {'type': 'string', 'readOnly': True}
        schema['properties'] = props

        return schema
