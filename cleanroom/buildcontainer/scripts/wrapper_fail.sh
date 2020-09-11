#!/bin/bash

echo "$@"
"$@"

EXIT_CODE=$?

if test $EXIT_CODE -ne 0 ; then
    echo "Fail shell after clrm finished with exit code ${EXIT_CODE}."
    /bin/bash
fi

exit $EXIT_CODE
