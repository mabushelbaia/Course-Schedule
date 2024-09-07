#! /usr/bin/env sh
set -e

# Check if the SSH_ENABLED environment variable is set to true ( currently disabled )
# if [ "$SSH_ENABLED" = "true" ]; then
#     apt-get update && apt-get install -y openssh-server && mkdir /var/run/sshd
# fi

# Start Gunicorn
exec gunicorn --worker-class uvicorn.workers.UvicornWorker --config='/app/gunicorn_conf.py' 'main:app'
