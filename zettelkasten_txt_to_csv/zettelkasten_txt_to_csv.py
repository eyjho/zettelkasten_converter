'''
Zettelkasten txt to csv converter
Eugene Ho, 11 Aug 2020

Read in .txt file copied from Evernote, separate into fields, and write csv for simple import to Google Sheets.

Data flow:
Read and decode .txt file
Extract subtitles and titles from zettel, with capitalisation
Extract fields (parent, UID = timestamp, title, contents, reference, keyword)
Check for duplicate keys, compiles index cards
Write to csv or text and save with same name + timestamp

Next steps
Accelerate timestamping

Future features:
Handle images
Read all files in directory
Adapt for .html output from Evernote or markdown
Read fields from list
Adapt for multi-depth list - currently forces everything into 2 layers
'''

import re
import os
import csv
import time
import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timezone

class Zettelkasten:

	def __init__(self, diagnostics = False):
		'''Initialise library[key = UID] of dictionaries[keys = parent, title, contents, reference, keyword]'''
		self.diagnostics = diagnostics # switch for diagnostics information
		self.library = {}
		self.master_key = 0
		self.file_path = ''


	def display(self):
		'''Show all zettels'''
		pass

	def tkgui_getfile(self, message = "Select file"):
		'''Select file with dialog and check'''
		if self.diagnostics:
			self.file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0_2.csv'

# 		'C:/Users/Eugene/Documents\
# /GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
			print(self.file_path)

		else:
			root = tk.Tk()
			root.withdraw()		
			self.file_path = filedialog.askopenfilename(
				initialdir = "..\\data",title = message)

		return self.file_path

	def split_path(self, path):
		'''os.path.splitext file path to separate path root and .extension'''
		# filename = re.split('/+|\\\\+|[.]', file_path)[-2] # to extract filename
		path_root, extension = os.path.splitext(path)
		# vulnerable to any periods in filename
		if self.diagnostics: print(new_path)
		return path_root, extension

	def import_csv_zk(self, library = None, file_path = None):
		'''Read csv file and save into memory'''
		# clean out library and check file type
		if library == None: library = dict()
		if file_path == None: file_path = self.file_path
		if not file_path.lower().endswith('.csv'):
			print('Error: Wrong filetype in importing .csv')
			return library

		with open(file_path, 'r', encoding = 'utf-8') as my_file:
			contents = csv.DictReader(my_file, delimiter=',')
			# row contains zettel dictionary
			for row in contents:
				text = ' '.join([f"[{field_name.lower()}] {contents}" \
					for field_name, contents in row.items()])
				if self.diagnostics: print("Imported dict: ", text)
				library = self.split_txt_to_dict(text, library,
					parent = '', field_type = 'zettel')
			my_file.close()
		return library

	def import_txt_to_str(self, file_path = None):
		'''Read txt file and return library'''
		# check file type
		if file_path == None: file_path = self.file_path
		if not file_path.lower().endswith('.txt'):
			print('Error: Wrong filetype in importing .txt')
			return library

		with open(file_path, 'r', encoding = 'utf-8') as my_file:
			contents = my_file.read()
			if self.diagnostics: print("During import \n", contents)
			my_file.close()

		return contents

	def split_str_text_to_lib(self, library = None, contents = ''):
		'''Separate text into library'''
		# Clean out library
		if library == None: library = dict()
		self.master_key = self.gsheets_timestamp)

		# Extract subsections from text into dictionary
		section_library = {}
		section_library = self.split_txt_to_dict(contents, section_library, parent = self.master_key, field_type = 'section')
		if self.diagnostics: print(len(section_library), " Sections extracted \n", section_library)
		
		library = self.split_section_lib_to_zettel_lib(section_library, library)

		if self.diagnostics:
			print("Library full")
			for key, value in library.items(): print(key, value)

		return library

	def split_section_lib_to_zettel_lib(self, section_library, library):
		'''Extract zettels from section dictionary into dictionary'''
		for key, sub_section in section_library.items():
			zettel_library = {} # Prevent RuntimeError: dictionary changed size during iteration
			zettel_library = self.split_txt_to_dict(sub_section['zettel'],
				zettel_library , parent = key, field_type = 'zettel')
			library.update({key: sub_section})
			library[key]['zettel'] = self.generate_index_text(zettel_library)
			library.update(zettel_library)
		return library

	def generate_index_text(self, zettel_library):
		'''Create index card text involving keys and titles of each component card'''
		index_contents = 'Section header. '
		for key, value in zettel_library.items():
			index_contents += f"{key}{', ' + value['title'] if value['title'] else ''}. "
		return index_contents

	def split_txt_to_dict(self, text, library = {}, parent = '', field_type = ''):
		'''Extract subsections from text into dictionary using regex
		text: string including contents of multiple fields
		library: to which fields will be added
		parent (previously section_key): manually specifies parent of zettel.
			Overwritten if parent in field_type
		field_type: index, parent, zettel, reference'''
		if 'section' in field_type:
			pattern = r'\n{2,3}[\w ]{1,100}\n{2,3}'
			parent = self.gsheets_timestamp)
		elif 'zettel' in field_type: pattern = r'\[\w{1,10}\]'
		else: print('Field type error'); return library

		search_results = re.finditer(pattern, text)

		# iterate through results and find each field marker
		key, library = self.sort_search_results_to_dict(
			text, library, search_results, field_type, parent)
		# clear empty entries
		library = {k: v for k, v in library.items() if v['zettel']}
		return library

	def sort_search_results_to_dict(self, text, library, search_results, field_type, parent):
		'''iterate through results and find each field marker to sort into library'''

		key, end_index, field_name, field_contents = 0, 0, '', ''

		for result in search_results:
			if self.diagnostics: print(f"Key: {key}, search result: {result}")
			
			# for sections, capture set of text before first subtitle
			if not end_index and 'section' in field_type:
				start_index, end_index, field_name = 0, 0, ''
			
			# exceptions for first result, just update field_name and indicies
			elif not end_index and 'zettel' in field_type: 
				field_name = result.group()
				start_index, end_index = result.span()
				continue # skip first instance

			# extract and clean field contents
			next_start_index = result.start()
			field_contents =  self.clean_text(text[end_index: next_start_index], False)
			start_index, end_index = result.span()

			# store field into library
			key, library = self.store_contents_to_lib(library, key, parent,
				field_name, field_contents, field_type)
			# update field_name
			field_name = self.clean_text(result.group(), False)

		# capture final entry
		field_contents = self.clean_text(text[end_index:-1], False)
		key, library = self.store_contents_to_lib(library, key, parent,
			field_name, field_contents, field_type)

		return key, library

	def store_contents_to_lib(self, library, key, parent, field_name, field_contents, field_type):
		'''Store zettelkasten contents or sections into fields in library'''
		if self.diagnostics: print('store_contents_to_lib: ', field_name, field_contents)
		# store in dictionary according to section or zettel
		if 'section' in field_type:
			key, library = self.store_subsections(library, parent, field_name, field_contents)
		elif 'zettel' in field_type:
			key, library = self.store_fields(library, key, parent, field_name, field_contents)
		
		return key, library

	def store_subsections(self, library = {}, parent = 0, field_name = '', field_contents = ''):
		'''Store chunk of text in dictionary with section heading as title and section as zettel'''
		key = self.gsheets_timestamp)
		if key in library.keys(): print('Error: Duplicate key while storing subsection')
		library[key] = dict(parent = parent, title = field_name,
			zettel = field_contents, reference = '', keyword = '')

		return key, library

	def store_fields(self, library = {}, key = 0, parent = 0, field_name = '', field_contents = ''):
		'''Store previously extracted zettelkasten into dictionary
		library: to which fields will be added
		key: index of zettel to which field belongs
		parent: manually specify parent field
		field_name: string - index, parent, zettel, reference
		field_contents: string body of field
		'''
		field_name = field_name.lower()

		if self.diagnostics: print(f"Key: {key}, field_name: {field_name}, contents: {field_contents}")

		if 'title' in field_name:
			library[key]['title'] = self.clean_text(field_contents, True)

		elif 'zettel' in field_name and ':' not in field_contents:
			library[key]['zettel'] = self.clean_text(field_contents, True)
		
		# split contents into title and zettel if colon present and title empty
		elif 'zettel' in field_name and ':' in field_contents and not library[key]['title']:
			if self.diagnostics: print('Splitting title')
			split_contents = re.split('[:]', field_contents)
			library[key]['title'] = self.clean_text(split_contents[0], True)
			library[key]['zettel'] = self.clean_text(split_contents[1], True)

		elif 'reference' in field_name:
			library[key]['reference'] = field_contents

		elif 'keyword' in field_name:
			library[key]['keyword'] = field_contents

		elif 'parent' in field_name:
			library[key]['parent'] = field_contents

		elif 'index' in field_name: # create new dictionary entry at each instance of 'index'
			key = self.gsheets_timestamp) if len(field_contents) < 3 else field_contents
			if key in library.keys(): print('Error: Duplicate key when assigning index')
			else: library[key] = dict(parent = parent, title = '', zettel = '', reference = '', keyword = '')
			if self.diagnostics: print("Index assigned: ", key, library[key])

		else: print('Error: Field not identified')

		return key, library

	def clean_text(self, text, capitals = False):
		'''Scrub string of double spaces, colons, and capitalize'''
		text = " ".join(text.split()) # remove double spaces

		if len(text) > 1: # empty/short strings create index errors
			text = text.translate(str.maketrans(';', ',')) # replace certain characters
			return text[0].upper() + text[1:] if capitals else text
		else: return text

	def gsheets_timestampself):
		'''Generate timestamp in Googlesheets format UTC (counts days from 30/12/1899)'''

		time.sleep(0.01) # 0.01s necessary to allow timestamp to update to new value
		python_timestamp = datetime.now(timezone.utc) - datetime(1899, 12, 30, tzinfo = timezone.utc)
		sheets_timestamp = python_timestamp.days + python_timestamp.seconds/(3600*24) + python_timestamp.microseconds/(3600*24*1000000)
		if self.diagnostics: print(python_timestamp.seconds)
		return '{:.8f}'.format(sheets_timestamp)

	def export_zk_csv(self, file_path, library):
		'''Write dictionary from memory to csv'''
		csv_output = open(file_path + '_' + str(self.master_key) + '.csv','w', newline='')
		csv_writer = csv.writer(csv_output , delimiter=';')

		for key, dictionary in library.items():
			csv_writer.writerow([key, dictionary['parent'], dictionary['title'], dictionary['zettel'], 
				dictionary['reference'], dictionary['keyword']])
		csv_output.close()
		return True

	def export_zk_txt(self, file_path, library):
		'''Write dictionary from memory to txt'''
		txt_output = open(file_path + '_' + str(self.master_key) + '.txt','w', newline='')
		for key, dictionary in library.items():
			txt_output.write(f"[index] {key} [parent] {dictionary['parent']} [title] {dictionary['title']}\
				\n[zettel] {dictionary['zettel']} \n[reference] {dictionary['reference']} \n[keyword] {dictionary['keyword']}\n\n")
		txt_output.close()
		pass

if __name__ == '__main__':
	zkn = Zettelkasten(diagnostics = False)
	# zkn.library = zkn.import_csv_zk()
	# file_path = zkn.tkgui_getfile()
	file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
	contents = ''
	contents = zkn.import_txt_to_str(file_path = file_path)
	zkn.library = zkn.split_str_text_to_lib(contents = contents)
	print(type(zkn.library))
	path_root, extension = zkn.split_path(file_path)
	print(path_root)
	# print(zkn.extract_filepath(path_root))
	# zkn.export_zk_csv(zkn.extract_filepath(filepath), zkn.library)
	# zkn.export_zk_txt(zkn.extract_filepath(filepath), zkn.library)
	# del zkn
	# zkn = Zettelkasten(diagnostics = False)
	# print(len(zkn.library))
	# zkn.library = zkn.import_txt_zk(file_path = file_path)
	# print(len(zkn.library))