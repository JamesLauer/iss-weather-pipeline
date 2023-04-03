#!/bin/bash
# Runs "cfn-lint", which is a CloudFormation template linter. This helps detect issues with
# the CloudFormation templates before trying to deploy with AWS SAM, therefore, saving
# time and headaches. See https://github.com/aws-cloudformation/cfn-lint for more
# information.

cd ..
echo "Linting CloudFormation templates...
"

# Run cfn-lint on the templates
if cfn-lint template.yaml app/**/*.yaml -i W; then
  echo "Linting completed successfully: no issues detected."
else
  echo "Linting failed: please fix the issues listed above."
  exit 1
fi

echo
echo "Warning: even if no issues are detected, it is common that the CloudFormation deployment will fail due to incorrect inputs or other issues that cannot be detected with the cfn-lint tool."
