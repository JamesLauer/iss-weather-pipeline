#!/bin/bash
# Runs "act", which simulates GitHub Actions by running locally in Docker. Instead of
# testing the GitHub Actions workflow in .github/workflow when committing and pushing to
# GitHub, it can be tested locally meaning that commits can be saved for workflows that work.
# See https://github.com/nektos/act for more information.

# Act is currently only set up to the run the unit and integration tests
cd ..
echo
echo "Running GitHub Actions locally in Docker
"
echo "Running unit and integration tests"
act -j run-unit-integration-tests

