#!/usr/bin/bash

FILE="${1}"

if test $(basename "${FILE}") == '__init__.py'; then
    exit 0
fi

echo "::::::::: ${FILE}:"
grep "import typing" "${FILE}" > /dev/null || echo "!!!!!!! ${FILE}: typing is not imported"
mypy "${FILE}"
