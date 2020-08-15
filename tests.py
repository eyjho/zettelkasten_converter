'''
Unit tests for Zettelkasten txt to csv converter
Eugene Ho, 14 Aug 2020

Following tutorial:
https://realpython.com/python-testing/#writing-your-first-test
'''

import unittest
from zettelkasten_txt_to_csv.zettelkasten_txt_to_csv import Zettelkasten

class TestZettelkasten(unittest.TestCase):
	'''Unit test for key functions of zettelkasten converter'''

	def setUp(self):
		'''Run before every subsequent test'''
		global zkn
		zkn = Zettelkasten(diagnostics = False)
		self.library_length = 73

	def test_template(self):
		'''Template "Zettelkasten v0_2.csv'''
		result = ''
		correct_answer = ''
		self.assertEqual(result, correct_answer)

	def test_find_file(self):
		'''Select "Zettelkasten v0_2.csv and return file_path'''
		result = zkn.find_file()
		correct_answer = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2.csv'
		self.assertEqual(result, correct_answer)

	def test_extract_filepath(self):
		'''Find filepath without ending'''
		# print('file_path: ', zkn.file_path) # zkn.file_path empty in test but fine in operation
		file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2.csv'
		result = zkn.extract_filepath(file_path)
		correct_answer = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2'
		self.assertEqual(result, correct_answer)

	def test_import_csv_length(self):
		'''Length of imported csv library should match row count'''
		file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2.csv'
		result = len(zkn.import_csv_zk(file_path = file_path))
		correct_answer = self.library_length
		self.assertEqual(result, correct_answer)

	def test_import_txt_length(self):
		'''Length of imported txt library should match row count'''
		file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
		result = len(zkn.import_txt_zk(file_path = file_path))
		correct_answer = self.library_length
		self.assertEqual(result, correct_answer)

	def test_txt_duplicates(self):
		'''Template "Zettelkasten v0_2.csv'''
		result = ''
		correct_answer = ''
		self.assertEqual(result, correct_answer)

	def tearDown(self):
		'''Run after every component test'''
		pass

if __name__ == '__main__':
	# zkn = Zettelkasten(diagnostics = False)
	loader = unittest.TestLoader()
	loader.sortTestMethodsUsing = None
	unittest.main(testLoader=loader)