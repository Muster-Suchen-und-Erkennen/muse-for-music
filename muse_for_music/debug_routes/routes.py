import urllib
from flask import render_template, url_for
from .. import app
from . import debug_blueprint


@debug_blueprint.route('/routes')
def routes():
    output = []
    for rule in app.url_map.iter_rules():

        options = {}
        print(rule.arguments)
        for arg in rule.arguments:
            if 'id' in arg:
                options[arg] = 0
                continue
            options[arg] = "{{{0}}}".format(arg)

        methods = ', '.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = {
            'endpoint': rule.endpoint,
            'methods': methods,
            'url': urllib.parse.unquote(url),
            'args': str(rule.arguments) if rule.arguments else '',
        }
        output.append(line)
        output.sort(key=lambda x: x['url'])
    return render_template('debug/routes/all.html',
                           title='muse4music – Routes',
                           routes=output)
