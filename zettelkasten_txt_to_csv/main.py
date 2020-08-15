#!/usr/bin/env python
# coding: utf-8

'''
Docstring
'''
from zettelkasten_txt_to_csv import Zettelkasten

if __name__ == '__main__':
	zkn = Zettelkasten(diagnostics = False)
	# zkn.library = zkn.import_csv_zk()
	# file_path = zkn.find_file()
	file_path = 'C:/Users/Eugene/Documents\
/GitHub/zettelkasten_txt_to_csv/data/00 Gardening zettlelkasten.txt'
	zkn.library = zkn.import_txt_zk(file_path = file_path)
	print(len(zkn.library))
	# filepath = zkn.file_path
	# print(filepath)
	# print(zkn.extract_filepath(file_path))
	# zkn.export_zk_csv(zkn.extract_filepath(filepath), zkn.library)
	# zkn.export_zk_txt(zkn.extract_filepath(filepath), zkn.library)
	del zkn
	zkn = Zettelkasten(diagnostics = False)
	print(len(zkn.library))
	zkn.library = zkn.import_txt_zk(file_path = file_path)
	print(len(zkn.library))