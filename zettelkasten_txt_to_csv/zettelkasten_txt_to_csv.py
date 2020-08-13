'''
Zettelkasten txt to csv converter
Eugene Ho, 11 Aug 2020

Read in .txt file copied from Evernote, separate into fields, and write csv for simple import to Google Sheets.

Data flow:
Read and decode .txt file
Extract fields (parent, UID = timestamp, title, contents, reference, keyword)
Extract subtitles and titles from zettel, with capitalisation
Write to csv and save with same name

Next steps
Order dictionary according to structure

Future features:
Automatically compile index cards
Export back into text
Duplicate key and field detection
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
/GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
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

	def import_zk(self, library = {}):
		'''Read file and save into memory'''
		# for .txt file
		if self.file_path.lower().endswith('.txt'): pass

		with open(self.file_path, 'r', encoding = 'utf-8') as my_file:
		    contents = my_file.read()
		    if self.diagnostics: print("During import \n", contents)
		    my_file.close()

		self.master_key = self.timestamp()

		# Extract subsections from text into dictionary
		section_library = {}
		section_library = self.separate_into_dictionary(contents, section_library, parent = self.master_key, field_type = 'section')
		if self.diagnostics: print("Sections extracted \n", section_library)
		zettel_library = {} # Prevent RuntimeError: dictionary changed size during iteration
		# Extract zettels from text into dictionary
		for key, sub_section in section_library.items():
			zettel_library = self.separate_into_dictionary(sub_section['zettel'],
				zettel_library , parent = key, field_type = 'zettel')
			library.update({key: sub_section})
			library[key]['zettel'] = 'Sub-section header'
			library.update(zettel_library)

		# Check for duplicates and merge dictionaries
		print('Duplicates: ', set(section_library.keys()).intersection(set(zettel_library.keys())))
		# if set(library.keys()).intersection(set(zettel_library.keys()):
		# 	print('Error: Duplicate keys')

		library.update(zettel_library)
		if self.diagnostics:
			print("Library full")
			for key, value in library.items(): print(key, value)
		return library

	def separate_into_dictionary(self, text, library = {}, parent = '', field_type = ''):
		'''Extract subsections from text into dictionary using regex'''

		if 'section' in field_type:
			pattern = r'\n{2,3}[\w ]{1,100}\n{2,3}'
			section_key = self.timestamp()
		elif 'zettel' in field_type: pattern = r'\[\w{1,10}\]'
		else: print('Field type error'); return library
		key, end_index, field_name, field_contents = 0, 0, '', ''
		search_results = re.finditer(pattern, text)

		# iterate through results and find each field marker
		for result in search_results:
			if self.diagnostics: print(result)
			
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
			field_contents =  self.clean_text(text[end_index: next_start_index])
			start_index, end_index = result.span()
			if self.diagnostics: print(result, '\n', start_index, field_name, field_contents)

			# store in dictionary according to section or zettel
			if 'section' in field_type:
				key, library = self.store_subsections(library, section_key, field_name, field_contents)
			elif 'zettel' in field_type:
				key, library = self.store_fields(library, key, parent, field_name, field_contents)
			
			# update field_name
			field_name = self.clean_text(result.group())

		# capture final entry
		field_contents = self.clean_text(text[end_index:-1])
		if self.diagnostics: print(field_contents)
		if 'section' in field_type:
			key, library = self.store_subsections(library, section_key, field_name, field_contents)
		elif 'zettel' in field_type:
			key, library = self.store_fields(library, key, parent, field_name, field_contents)
		# clear empty entries
		library = {k: v for k, v in library.items() if v['zettel']}
		return library

	def store_subsections(self, library = {}, parent = 0, field_name = '', field_contents = ''):
		'''Store in dictionary with section heading as title and section as zettel'''
		key = self.timestamp()
		if key in library.keys(): print('Error')
		library[key] = dict(parent = parent, title = field_name,
			zettel = field_contents, reference = '', keyword = '')

		return key, library

	def store_fields(self, library = {}, key = 0, parent = 0, field_name = '', field_contents = ''):
		'''Store previously extracted zettelkasten into dictionary'''

		if self.diagnostics: print(key, field_name, field_contents)

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

		elif 'index' in field_name: # create new dictionary entry at each instance of 'index'
			key = self.timestamp()
			if key in library.keys(): print('Error')
			library[key] = dict(parent = parent, title = '', zettel = '', reference = '', keyword = '')
			if self.diagnostics: print(library[key])

		return key, library

	def clean_text(self, text, capitals = False):
		'''Scrub string of double spaces etc'''
		if len(text) > 0: # empty/short strings create index errors
			text = text.translate(str.maketrans(';', ',')) # replace certain characters
			text = text[0].upper() + text[1:]
			return " ".join(text.split())
		else: return text

	def timestamp(self):
		'''Generate timestamp in Googlesheets format UTC (counts days from 30/12/1899)'''

		time.sleep(0.01) # 0.01s necessary to allow timestamp to update to new value
		python_timestamp = datetime.now(timezone.utc) - datetime(1899, 12, 30, tzinfo = timezone.utc)
		sheets_timestamp = python_timestamp.days + python_timestamp.seconds/(3600*24) + python_timestamp.microseconds/(3600*24*1000000)
		if self.diagnostics: print(python_timestamp.seconds)
		return '{:.8f}'.format(sheets_timestamp, 6)

	def extract_filepath(self, file_path):
		'''re.split() file path to pick out filepath without ending'''
		# filename = re.split('/+|\\\\+|[.]', file_path)[-2] # to extract filename
		new_path = re.split('[.]', file_path)[-2]
		if self.diagnostics: print(new_path)
		return new_path

	def export_zk(self, file_path, library):
		'''Write dictionary from memory to csv'''
		csv_output = open(file_path + '_' + str(self.master_key) + '.csv','w', newline='')
		csv_writer = csv.writer(csv_output , delimiter=';')

		for key, dictionary in library.items():
			csv_writer.writerow([key, dictionary['parent'], dictionary['title'], dictionary['zettel'], 
				dictionary['reference'], dictionary['keyword']])
		csv_output.close()
		return True