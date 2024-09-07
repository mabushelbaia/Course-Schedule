from __future__ import print_function

import json
import multiprocessing
import os

use_loglevel = os.getenv("LOG_LEVEL", "info")

# Gunicorn config variables
loglevel = use_loglevel
bind = "0.0.0.0:8000"
keepalive = 120
errorlog = "-"  # stdout

# https://docs.gunicorn.org/en/latest/design.html#how-many-workers
cores = multiprocessing.cpu_count()

workers = 2 * cores + 1


# for debugging
log_data = {
    "loglevel": loglevel,
    "workers": workers,
    "bind": bind,
}
print("Gunicorn config: " + json.dumps(log_data))
