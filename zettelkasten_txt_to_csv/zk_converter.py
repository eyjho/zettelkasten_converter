'''
Zettelkasten converter
Eugene Ho, 17 Aug 2020

Convert zettelkasten between txt and csv

Next steps
Accelerate timestamping
'''

import re
import os
import csv
import time
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timezone

class Controller:
	'''Provide GUI to choose file and split into path root and extension'''

	def __init__(self):
		self.file_path = ''

	def tkgui_getfile(self, message = "Select file"):
		'''Select file with dialog and check'''
		root = tk.Tk(); root.withdraw()		
		self.file_path = filedialog.askopenfilename(
			initialdir = "..\\data",title = message)

		return self.file_path

	def split_path(self, path):
		'''os.path.splitext file path to separate path root and .extension'''
		path_root, extension = os.path.splitext(path)
		return path_root, extension

class Zettel:
	'''Import and export information for one zettel with index as variable name'''

	def __init__(self):
		self.parent = ''
		self.title = ''
		self.zettel = ''
		self.reference = ''
		self.keyword = ''
		self.type = ''

	def __str__(self):
		return f"[parent] {self.parent} [title] {self.title}\
				\n[zettel] {self.zettel} \n[reference] {self.reference} \n[keyword] {self.keyword}"

	def clean_text(self, text, capitals = False):
		'''Scrub string of double spaces, colons, and capitalize'''
		text = " ".join(text.split()) # remove double spaces

		if len(text) > 1: # empty/short strings create index errors
			text = text.translate(str.maketrans(';', ',')) # replace certain characters
			return text[0].upper() + text[1:] if capitals else text
		else: return text

	def store_index_zettel(self, library, parent, field_name, field_contents):
		'''Store previously extracted section contents into zettel'''
		self.parent = parent
		self.title = field_name.lower()
		self.zettel = field_contents
		self.type = 'section'

	def store_zettel_field(self, library = {}, key = 0, parent = 0, field_name = '', field_contents = ''):
		'''Store previously extracted zettelkasten into dictionary
		library: to which fields will be added
		key: index of zettel to which field belongs
		parent: manually specify parent field
		field_name: string - index, parent, zettel, reference
		field_contents: string body of field
		'''
		field_name = field_name.lower()
		# print('store_zettel_field: ', field_name)#, field_contents)

		if 'title' in field_name:
			self.title = self.clean_text(field_contents, True)

		elif 'zettel' in field_name and ':' not in field_contents:
			self.zettel = self.clean_text(field_contents, True)
		
		# split contents into title and zettel if colon present and title empty
		elif 'zettel' in field_name and ':' in field_contents and not self.title:
			split_contents = re.split('[:]', field_contents)
			self.title = self.clean_text(split_contents[0], True)
			self.zettel = self.clean_text(split_contents[1], True)

		elif 'reference' in field_name:
			self.reference = field_contents

		elif 'keyword' in field_name:
			self.keyword = field_contents

		elif 'parent' in field_name:
			self.parent = field_contents

		else: print(f'Error: Field {field_name} not identified')

class Zettelkasten(Zettel):
	'''Convert zettelkasten between txt and csv formats'''

	def __init__(self, diagnostics = False):
		'''Initialise library[key = UID] of dictionaries[keys = parent, title, contents, reference, keyword]'''
		self.diagnostics = diagnostics # switch for diagnostics information
		self.library = {}
		self.master_key = 0

	def display(self, quantity, start_index = 0):
		'''Show some number of zettels'''
		for key, value in list(self.library.items())[start_index:start_index+quantity]:
			print(f"[index] {key} [parent] {value.parent} [title] {value.title}")

	def import_txt_to_str(self, file_path = ''):
		'''Read txt file and return library'''
		# check file type
		if not file_path.lower().endswith('.txt'):
			print('Error: Wrong filetype in importing .txt')
			return library

		with open(file_path, 'r', encoding = 'utf-8') as my_file:
			contents = my_file.read()
			if self.diagnostics: print("During import \n", contents)
			my_file.close()

		return contents

	def find_sections_in_txt(self, contents, library = {}, parent = '', field_type = ''):
		'''Extract subsections as search results from text using regex'''
		if 'section' in field_type:
			pattern = r'\n{2,3}[\w ]{1,100}\n{2,3}'
		elif 'zettel' in field_type:
			pattern = r'\[\w{1,10}\]'
			# parent = self.gsheets_timestamp() # temp
		else: print('Field type error'); return None

		search_results = re.finditer(pattern, contents)
		return search_results

	def sort_search_results_to_tuple(self, contents, search_results):
		'''Iterate results and find each field marker to sort into tuple'''

		key, end_index, field_name, field_contents = 0, 0, '', ''
		fields_out_list = []

		for result in search_results:
			if self.diagnostics: print(f"Key: {key}, search result: {result}")

			# for sections, capture set of text before first subtitle
			if not end_index:
				start_index, end_index, field_name = 0, 0, ''

			# extract, clean, yield field contents
			next_start_index = result.start()
			field_contents =  self.clean_text(contents[end_index: next_start_index], False)
			start_index, end_index = result.span()
			yield field_name, field_contents

			# update field_name
			field_name = self.clean_text(result.group(), False)

		# capture final entry
		field_contents = self.clean_text(contents[end_index:-1], False)
		yield field_name, field_contents
		# key, library = self.store_contents_to_lib(library, key, parent,
			# field_name, field_contents, field_type)

	def store_tuple_to_lib(self, fields_tuple, field_type, library = None, key = 0, parent = 0):
		'''Store zettelkasten contents or sections into fields in library'''
		if library == None: library = dict()
		# print('Fields_tuple: ', fields_tuple)

		field_name, field_contents = fields_tuple
		# store in dictionary according to section or zettel
		# print('store_list_to_lib: ', field_name, field_contents)
		if 'section' in field_type:
			parent = self.gsheets_timestamp()
			key, library = self.store_subsections(library, parent, field_name, field_contents)
		elif not field_name: pass
		elif 'zettel' in field_type and 'index' in field_name:
		# create new dictionary entry at each instance of 'index'
			key = self.gsheets_timestamp() if len(field_contents) < 5 else field_contents
			if key in library.keys(): print('Error: Duplicate key when assigning index')
			else: library[key] = Zettel(); library[key].parent = parent
			if self.diagnostics: print("Index assigned: ", key, library[key])
		elif 'zettel' in field_type and key:
			library[key].store_zettel_field(library, key, parent, field_name, field_contents)
		else: print(f'Error: Field type {field_type} not recognised')
		
		return key, library

	def split_section_lib(self, contents):
		field_type, field_lib, library, key = 'zettel', dict(), dict(), 0
		search_results = self.find_sections_in_txt(contents, field_type = field_type)
		results_generator = self.sort_search_results_to_tuple(contents, search_results)
		for fields_tuple in results_generator:
			key, field_lib = self.store_tuple_to_lib(fields_tuple, field_type, field_lib, key)
			library.update(field_lib)

		# clear empty entries
		library = {k: v for k, v in library.items() if v.zettel}
		return library

	def gsheets_timestamp(self):
		'''Generate timestamp in Googlesheets format UTC (counts days from 30/12/1899)'''

		time.sleep(0.01) # 0.01s necessary to allow timestamp to update to new value
		python_timestamp = datetime.now(timezone.utc) - datetime(1899, 12, 30, tzinfo = timezone.utc)
		sheets_timestamp = python_timestamp.days + python_timestamp.seconds/(3600*24) + python_timestamp.microseconds/(3600*24*1000000)
		if self.diagnostics: print(python_timestamp.seconds)
		return '{:.8f}'.format(sheets_timestamp)


if __name__ == '__main__':
	zkn = Zettelkasten(diagnostics = False)
	controller = Controller()
	# file_path = controller.tkgui_getfile()
	file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
	contents = zkn.import_txt_to_str(file_path = file_path)
	zkn.library = zkn.split_section_lib(contents)

	zkn.display(20)
	print(len(zkn.library))