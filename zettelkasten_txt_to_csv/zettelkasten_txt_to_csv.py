'''
Zettelkasten txt to csv converter
Eugene Ho, 11 Aug 2020

Read in .txt file copied from Evernote, separate into fields, and write csv for simple import to Google Sheets.

Data flow:
Read and decode .txt file
Extract fields (parent, UID = timestamp, title, contents, reference, keyword)
Write to csv and save with same name

Next steps
Extract titles from zettel
Subtitles are imported as index card titles

Future features:
Read all files in directory
Adapt for .html output from Evernote or markdown
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
		self.zettel_library = {}
		self.file_path = 'C:/Users/Eugene/Documents/GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'

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

	def import_zk(self):
		'''Read file and save into memory'''
		# for .txt file
		if self.file_path.lower().endswith('.txt'): pass

		with open(self.file_path, 'r', encoding = 'utf-8') as my_file:
		    contents = my_file.read()
		    if self.diagnostics: print(contents)
		    my_file.close()

		if self.diagnostics:
			for key, value in self.separate_fields(contents).items(): print(key, value)

		return self.separate_fields(contents)

	def separate_fields(self, text, library = {}):
		'''Extract fields from text into dictionary using regex'''
		key, end_index = 0, 0
		field_name, field_contents = '', ''
		pattern = r'\[\w{1,10}\]'
		search_results = re.finditer(pattern, text)

		# iterate through results and find each field marker
		for result in search_results:
			# exceptions for first result, just update field_name and indicies
			if not end_index:
				start_index, end_index = result.span()
				field_name = result.group()
				continue # skip first instance
			
			# extract and clean field contents
			next_start_index = result.start()
			field_contents = self.clean_text(text[end_index: next_start_index])
			start_index, end_index = result.span()
			if self.diagnostics: print(result, '\n', start_index, field_name, field_contents)

			# store previously extracted contents into dictionary
			if 'zettel' in field_name:
				library[key]['zettel'] = field_contents

			elif 'reference' in field_name:
				library[key]['reference'] = field_contents

			elif 'keyword' in field_name:
				library[key]['keyword'] = field_contents

			elif 'index' in field_name: # create new dictionary entry at each instance of 'index'
				key = self.timestamp()
				if key in library.keys(): print('Error')
				library[key] = dict(parent = '', title = '')

			# update field_name
			field_name = self.clean_text(result.group())

		# capture final entry
		next_start_index = result.start()
		field_contents = self.clean_text(text[end_index: next_start_index])
		if 'keyword' in field_name:
			library[key]['keyword'] = field_contents

		# clear empty entries
		library = {k: v for k, v in library.items() if v['zettel']}
		# try: library = {k: v for k, v in dictionary.items() if v['zettel']}
		# except: print("Dictionary library error")
		if self.diagnostics:
			for k, v in library.items():
				dictionary = v
				print(k, dictionary.keys())
		return library

	def clean_text(self, text):
		'''Scrub string of double spaces etc'''
		text = text.translate(str.maketrans(';', ',')) # replace certain characters
		return " ".join(text.split())

	def timestamp(self):
		'''Generate timestamp in Googlesheets format UTC (counts days from 30/12/1899)'''

		time.sleep(0.01) # necessary to allow timestamp to update to new value
		python_timestamp = datetime.now(timezone.utc) - datetime(1899, 12, 30, tzinfo = timezone.utc)
		sheets_timestamp = python_timestamp.days + python_timestamp.seconds/(3600*24) + python_timestamp.microseconds/(3600*24*1000000)
		if self.diagnostics: print(python_timestamp.seconds)
		return '{:.8f}'.format(sheets_timestamp, 6)

	def extract_filepath(self, file_path):
		'''re.split() file path to pick out filename'''
		# filename = re.split('/+|\\\\+|[.]', file_path)[-2] # to extract filename
		filename = re.split('[.]', file_path)[-2]
		if self.diagnostics: print(filename)
		return filename

	def export_zk(self, filename, library):
		'''Write dictionary from memory to csv'''
		csv_output = open(filename + '.csv','w', newline='')
		csv_writer = csv.writer(csv_output , delimiter=';')

		for key, dictionary in library.items():
			csv_writer.writerow([key, dictionary['parent'], dictionary['title'], dictionary['zettel'], 
				dictionary['reference'], dictionary['keyword']])
		csv_output.close()
		return True

if __name__ == '__main__':
	zettelkasten = Zettelkasten(diagnostics = True)
	# zettelkasten.find_file()
	zettelkasten.zettel_library = zettelkasten.import_zk()
	# print(zettelkasten.timestamp())
	filepath = zettelkasten.file_path
	# zettelkasten.extract_filepath(filepath)
	zettelkasten.export_zk(zettelkasten.extract_filepath(filepath), zettelkasten.zettel_library)
