#!/bin/sh

echo "Demo OpenModelica executable"
echo "Received arguments: $*"

case "$1" in
  -override=*)
    echo "Simulation launched with override flag."
    exit 0
    ;;
  *)
    echo "Expected an OpenModelica -override argument." >&2
    exit 1
    ;;
esac
