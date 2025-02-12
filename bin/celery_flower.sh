#!/bin/bash
exec celery --app woo_search.celery --workdir src flower
