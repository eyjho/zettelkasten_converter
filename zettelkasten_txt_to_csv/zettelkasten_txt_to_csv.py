'''
Zettelkasten txt to csv converter
Eugene Ho, 11 Aug 2020

Read in .txt file copied from Evernote, separate into fields, and write csv for simple import to Google Sheets.

Data flow:
Read and decode .txt file
Extract subtitles and titles from zettel, with capitalisation
Extract fields (parent, UID = timestamp, title, contents, reference, keyword)
Check for duplicate keys
Write to csv and save with same name

Next steps

Future features:
Automatically compile index cards
Check for duplicate zettels
Export back into text
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
		if self.diagnostics: self.file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/Zettelkasten v0.2 - main.csv'

# 		'C:/Users/Eugene/Documents\
# /GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
		else: self.file_path = self.find_file()
		self.master_key = 0

	def __str__(self):
		'''Show some stats (number of dictionaries)'''
		pass

	def display(self):
		'''Show all zettels'''
		pass

	def find_file(self):
		'''Select and check file'''
		root = tk.Tk()
		root.withdraw()

		self.file_path = filedialog.askopenfilename()
		if self.diagnostics: print(self.file_path)
		return self.file_path

	def import_csv_zk(self, library = {}):
		'''Read csv file and save into memory'''
		# check file type
		if not self.file_path.lower().endswith('.csv'):
			print('Filetype error')
			return False

		with open(self.file_path, 'r', encoding = 'utf-8') as my_file:
			contents = csv.DictReader(my_file, delimiter=',')

			# row contains zettel dictionary
			for row in contents:
				text = ' '.join([f"[{field_name.lower()}] {contents}" for field_name, contents in row.items()])
				if self.diagnostics: print("Imported dict: ", text)
				library = self.separate_into_dictionary(text, library, parent = '', field_type = 'zettel')
				# key = 0
				# # iterate through dictionary and let self.store_fields identify ands store each field
				# for field_name in row:
				# 	# print(item, row[item])
				# 	text = f"[{field_name.lower()}] {row[field_name]}"
				# 	print('Imported row from csv', text)
				# 	key, library = self.store_fields(library, key, field_name = field_name, field_contents = row[field_name])
			my_file.close()
		return library

	def import_txt_zk(self, library = {}):
		'''Read txt file and save into memory'''
		# check file type
		if not self.file_path.lower().endswith('.txt'):
			print('Filetype error')
			return False

		with open(self.file_path, 'r', encoding = 'utf-8') as my_file:
		    contents = my_file.read()
		    if self.diagnostics: print("During import \n", contents)
		    my_file.close()

		self.master_key = self.timestamp()

		# Extract subsections from text into dictionary
		section_library = {}
		section_library = self.separate_into_dictionary(contents, section_library, parent = self.master_key, field_type = 'section')
		if self.diagnostics: print("Sections extracted \n", section_library)
		
		# Extract zettels from text into dictionary
		for key, sub_section in section_library.items():
			zettel_library = {} # Prevent RuntimeError: dictionary changed size during iteration
			zettel_library = self.separate_into_dictionary(sub_section['zettel'],
				zettel_library , parent = key, field_type = 'zettel')
			library.update({key: sub_section})
			library[key]['zettel'] = self.generate_index_text(zettel_library)
			library.update(zettel_library)

			# Check for duplicates and merge dictionaries
			print('Duplicates: ', set(section_library.keys()).intersection(set(zettel_library.keys())))

		if self.diagnostics:
			print("Library full")
			for key, value in library.items(): print(key, value)
		return library

	def generate_index_text(self, zettel_library):
		'''Create index card text involving keys and titles of each component card'''
		index_contents = 'Section header. '
		for key, value in zettel_library.items():
			index_contents += f"{key}{', ' + value['title'] if value['title'] else ''}. "
		return index_contents

	def separate_into_dictionary(self, text, library = {}, parent = '', field_type = ''):
		'''Extract subsections from text into dictionary using regex
		text: string including contents of multiple fields
		library: to which fields will be added
		parent: manually specifies parent of zettel. Overwritten if parent in field_type
		field_type: index, parent, zettel, reference'''
		if 'section' in field_type:
			pattern = r'\n{2,3}[\w ]{1,100}\n{2,3}'
			section_key = self.timestamp()
		elif 'zettel' in field_type: pattern = r'\[\w{1,10}\]'
		else: print('Field type error'); return library
		key, end_index, field_name, field_contents = 0, 0, '', ''
		search_results = re.finditer(pattern, text)

		# iterate through results and find each field marker
		for result in search_results:
			if self.diagnostics: print(f"Key: {key}, search result: {result}")
			
			# for sections, capture set of text before first subtitle
			if not end_index and 'section' in field_type:
				start_index, end_index = 0, 0
				field_name = ''
			
			# exceptions for first result, just update field_name and indicies
			elif not end_index and 'zettel' in field_type: 
				field_name = result.group()
				start_index, end_index = result.span()
				continue # skip first instance

			# extract and clean field contents
			next_start_index = result.start()
			field_contents =  self.clean_text(text[end_index: next_start_index], False)
			start_index, end_index = result.span()
			if self.diagnostics: print(result, '\n', start_index, field_name, field_contents)

			# store in dictionary according to section or zettel
			if 'section' in field_type:
				key, library = self.store_subsections(library, section_key, field_name, field_contents)
			elif 'zettel' in field_type:
				key, library = self.store_fields(library, key, parent, field_name, field_contents)
			
			# update field_name
			field_name = self.clean_text(result.group(), False)

		# capture final entry
		field_contents = self.clean_text(text[end_index:-1], False)
		if self.diagnostics: print(field_contents)
		if 'section' in field_type:
			key, library = self.store_subsections(library, section_key, field_name, field_contents)
		elif 'zettel' in field_type:
			key, library = self.store_fields(library, key, parent, field_name, field_contents)
		# clear empty entries
		library = {k: v for k, v in library.items() if v['zettel']}
		return library

	def store_subsections(self, library = {}, parent = 0, field_name = '', field_contents = ''):
		'''Store chunk of text in dictionary with section heading as title and section as zettel'''
		key = self.timestamp()
		if key in library.keys(): print('Error: Duplicate key while storing subsection')
		library[key] = dict(parent = parent, title = field_name,
			zettel = field_contents, reference = '', keyword = '')

		return key, library

	def store_fields(self, library = {}, key = 0, parent = 0, field_name = '', field_contents = ''):
		'''Store previously extracted zettelkasten into dictionary
		library: to which fields will be added
		parent: manually specify parent field
		field_name: string - index, parent, zettel, reference
		field_contents: string body of field
		'''

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
			key = self.timestamp() if len(field_contents) < 3 else field_contents
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

	def timestamp(self):
		'''Generate timestamp in Googlesheets format UTC (counts days from 30/12/1899)'''

		time.sleep(0.01) # 0.01s necessary to allow timestamp to update to new value
		python_timestamp = datetime.now(timezone.utc) - datetime(1899, 12, 30, tzinfo = timezone.utc)
		sheets_timestamp = python_timestamp.days + python_timestamp.seconds/(3600*24) + python_timestamp.microseconds/(3600*24*1000000)
		if self.diagnostics: print(python_timestamp.seconds)
		return '{:.8f}'.format(sheets_timestamp)

	def extract_filepath(self, file_path):
		'''re.split() file path to pick out filepath without ending'''
		# filename = re.split('/+|\\\\+|[.]', file_path)[-2] # to extract filename
		new_path = re.split('[.]', file_path)[-2]
		if self.diagnostics: print(new_path)
		return new_path

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