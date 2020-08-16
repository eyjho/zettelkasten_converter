'''
Test suite runner for Zettelkasten txt to csv converter
Eugene Ho, 15 Aug 2020

Following tutorial:
https://www.internalpointers.com/post/run-painless-test-suites-python-unittest
'''

import unittest
import tests
from zettelkasten_txt_to_csv.zettelkasten_txt_to_csv import Zettelkasten

def suite():
	suite = unittest.TestSuite()
	suite.addTest(loader.loadTestsFromModule(tests))
	return suite

if __name__ == '__main__':
	loader = unittest.TestLoader()
	loader.sortTestMethodsUsing = None
	runner = unittest.TextTestRunner(verbosity=1)
	result = runner.run(suite())