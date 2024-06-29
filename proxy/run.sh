#!/bin/sh

set -e

envsubst < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'