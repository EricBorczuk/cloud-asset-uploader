import cherrypy
from contextlib import contextmanager

@contextmanager
def run_server():
    cherrypy.engine.start()
    cherrypy.engine.wait(cherrypy.engine.states.STARTED)
    try:
        yield
    finally:
        cherrypy.engine.exit()
