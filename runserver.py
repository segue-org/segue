from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple

import segue

backend = segue.Application()
null    = segue.NullApplication()

application = DispatcherMiddleware(null, {
    '/api': backend
})

if __name__ == "__main__":
    run_simple('0.0.0.0', 5000, application, use_reloader=True, use_debugger=True)

