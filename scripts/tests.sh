#!/bin/bash

# Based on https://github.com/commitizen-tools/commitizen/blob/master/scripts/test

export PREFIX="poetry run python -m "
if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

${PREFIX}pytest --cov-report=xml:coverage.xml --cov=seaport tests/
poetry check
${PREFIX}black --check .
${PREFIX}isort --check-only .
# TODO: Type check tests
${PREFIX}mypy --strict seaport
${PREFIX}pydocstyle --convention=google