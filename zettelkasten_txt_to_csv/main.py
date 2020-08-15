#!/usr/bin/env python
# coding: utf-8

'''
Docstring
'''
from zettelkasten_txt_to_csv import Zettelkasten

if __name__ == '__main__':
	zkn = Zettelkasten(diagnostics = False)
	zkn.library = zkn.import_csv_zk()
	# zkn.library = zkn.import_txt_zk()
	# print(len(zkn.library))
	filepath = zkn.file_path
	print(filepath)
	# zkn.export_zk_csv(zkn.extract_filepath(filepath), zkn.library)
	# zkn.export_zk_txt(zkn.extract_filepath(filepath), zkn.library)