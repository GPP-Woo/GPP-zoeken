#!/bin/bash

set -e

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

mkdir -p celerybeat

echo "Starting celery beat"
exec celery --workdir src --app woo_search.celery beat \
    -l $LOGLEVEL \
    -s ../celerybeat/beat
