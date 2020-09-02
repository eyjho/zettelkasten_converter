#!/usr/bin/env python
# coding: utf-8

'''
Docstring
'''
from zettelkasten_converter import Zettelkasten

if __name__ == '__main__':
	zkn = Zettelkasten(diagnostics = False)
	file_path = zkn.find_file()
	zkn.library = zkn.import_txt_zk(file_path = file_path)
	zkn.export_zk_csv(zkn.extract_filepath(file_path), zkn.library)