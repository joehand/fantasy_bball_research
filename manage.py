# manage.py
import os
import logging

from flask import url_for

from fantasy import create_app
from fantasy.config import ProductionConfig, DevelopmentConfig

from flask_script import Manager, Shell


if os.environ.get('PRODUCTION'):
    app = create_app(config = ProductionConfig)
else:
    app = create_app()

manager = Manager(app)


@manager.command
def routes():
    """ Prints out all the routes to shell
    """
    import urllib.request, urllib.parse, urllib.error
    output = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        methods = ','.join(rule.methods)
        url = url_for(rule.endpoint, **options)
        line = urllib.parse.unquote("{:50s} {:20s} {}".format(rule.endpoint, methods, url))
        output.append(line)
    for line in sorted(output):
        print (line)

def shell_context():
    return dict(app=app)

#runs the app
if __name__ == '__main__':
    manager.add_command('shell', Shell(make_context=shell_context))
    manager.run()
