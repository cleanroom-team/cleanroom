#!/bin/bash

"$@"

EXIT_CODE=$?

echo "Post shell after clrm finished with exit code ${EXIT_CODE}"

/bin/bash

exit ${EXIT_CODE}
