#!/bin/bash
# Analyses the projects Python lambda_functions in terms of cyclomatic complexity and
# test coverage. Requires pip install of radon, coverage and moto to run script.
cd ..
echo "Calculating cyclomatic complexity
"
radon cc app/lambdas/functions/*.py -s
echo "
Running unit tests and then determining coverage
"
coverage run -m unittest discover
coverage report -m