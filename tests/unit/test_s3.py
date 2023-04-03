import re
import unittest
from app.lambdas.functions.s3 import (
	count_objects_in_s3_prefix,
	)


class TestPutObjectInS3Bucket(unittest.TestCase):
	# Tests the put_object_in_s3_bucket function
	
	def test_date_format_is_correct(self):
		# Tests that the date format in the function is correct, if not then function
		# will fail
		# Defines the expected date format
		expected_date_format = r"year=%Y/month=%m/day=%d"
		
		# Gets the actual date format used in the function
		actual_date_format = str(count_objects_in_s3_prefix.__code__.co_consts[2])
		
		# Uses regular expressions to check if the date format is correct
		self.assertTrue(
			re.match(expected_date_format, actual_date_format),
			f"Date format mismatch, expected: {expected_date_format}, actual: "
			f" {actual_date_format}"
			)


if __name__ == '__main__':
	unittest.main()
