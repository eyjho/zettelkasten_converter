'''
Unit tests for Zettelkasten txt to csv converter
Eugene Ho, 14 Aug 2020

Following tutorial:
https://realpython.com/python-testing/#writing-your-first-test
'''

import unittest
from zettelkasten_txt_to_csv.zk_converter import Zettelkasten, Controller

class TestZettelkasten(unittest.TestCase):
	'''Unit test for key functions of zettelkasten converter'''

	def setUp(self):
		'''Run before every subsequent test'''
		global zkn, controller
		zkn = Zettelkasten(diagnostics = False)
		controller = Controller()
		self.library_length = 73

	def test_template(self):
		'''Template "Zettelkasten v0_2.csv'''
		result = ''
		correct_answer = ''
		self.assertEqual(result, correct_answer)

	def test_tkgui_getfile(self):
		'''Select "Zettelkasten v0_2.csv and return file_path'''
		result = controller.tkgui_getfile('Select Zettelkasten v0_2.csv')
		correct_answer = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2.csv'
		self.assertEqual(result, correct_answer)

	def test_split_path(self):
		'''Find filepath without ending'''
		# print('file_path: ', zkn.file_path) # zkn.file_path empty in test but fine in operation
		file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2.csv'
		result, extension = controller.split_path(file_path)
		correct_answer = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2'
		self.assertEqual(result, correct_answer)

	def tearDown(self):
		'''Run after every component test'''
		global zkn
		del zkn

class TestZkn_CSV(unittest.TestCase):
	'''Unit test for csv import of zettelkasten converter'''

	def setUp(self):
		'''Run before every subsequent test'''
		global zkn
		zkn = Zettelkasten(diagnostics = False)
		file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2.csv'
		zkn.library = zkn.run_csv(file_path = file_path)
		self.library_length = 73

	def test_run_csv_length(self):
		'''Length of imported txt library should match row count'''
		result = len(zkn.library)
		correct_answer = self.library_length
		self.assertEqual(result, correct_answer)

	def test_duplicates(self):
		'''Check keys are unique'''
		result = len(zkn.library)
		correct_answer = len(set(zkn.library))
		self.assertEqual(result, correct_answer)

	def tearDown(self):
		'''Run after every component test'''
		global zkn
		del zkn

class TestZkn_TXT(unittest.TestCase):
	'''Unit test for text import of zettelkasten converter'''

	def setUp(self):
		'''Run before every subsequent test'''
		global zkn, file_path
		zkn = Zettelkasten(diagnostics = False)
		file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
		self.library_length = 73
		self.section_num = 7

	def test_run_txt_length(self):
		'''Length of imported txt library should match row count'''
		zkn.library = zkn.run_txt(file_path)
		result = len(zkn.library)
		correct_answer = self.library_length
		self.assertEqual(result, correct_answer)

	def test_import_section_length(self):
		'''Length of imported txt library should match row count'''
		contents = zkn.import_txt_to_str(file_path = file_path)
		parent, field_type = zkn.gsheets_timestamp(), 'section'
		section_zettel_generator = zkn.split_generator(contents, field_type, parent)
		result = sum([1 for _ in section_zettel_generator])
		correct_answer = self.section_num
		self.assertEqual(result, correct_answer)

	def test_duplicates(self):
		'''Check keys are unique'''
		result = len(zkn.library)
		correct_answer = len(set(zkn.library))
		self.assertEqual(result, correct_answer)

	def tearDown(self):
		'''Run after every component test'''
		global zkn
		del zkn

if __name__ == '__main__':
	# zkn = Zettelkasten(diagnostics = False)
	loader = unittest.TestLoader()
	loader.sortTestMethodsUsing = None
	unittest.main(testLoader=loader)