from werkzeug.debug import DebuggedApplication
from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple

import lib

backend = lib.Application()
null = lib.NullApplication()

application = DispatcherMiddleware(null, {
    '/api': backend
})

if __name__ == "__main__":
    run_simple('0.0.0.0', 5000, application, use_reloader=True, use_debugger=True)

