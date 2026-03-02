#!/usr/bin/env bash

set -e

if [ $# -lt 3 ]; then
  echo "Usage: $0 host:port -- command [args...]"
  exit 1
fi

HOST_PORT="$1"
shift

IFS=':' read -r WAIT_HOST WAIT_PORT <<< "$HOST_PORT"

if [ -z "$WAIT_HOST" ] || [ -z "$WAIT_PORT" ]; then
  echo "Error: host and port must be in the form host:port"
  exit 1
fi

echo "Waiting for $WAIT_HOST:$WAIT_PORT ..."
until (echo >/dev/tcp/"$WAIT_HOST"/"$WAIT_PORT") >/dev/null 2>&1; do
  sleep 1
done
echo "$WAIT_HOST:$WAIT_PORT is available."

if [ "$1" != "--" ]; then
  echo "Error: expected -- before command"
  exit 1
fi
shift

exec "$@"

