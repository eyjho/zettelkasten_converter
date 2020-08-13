#!/usr/bin/env python
# coding: utf-8

'''
Docstring
'''
from zettelkasten_txt_to_csv import Zettelkasten

if __name__ == '__main__':
	zettelkasten = Zettelkasten(diagnostics = False)
	# zettelkasten.find_file()
	zettelkasten.zettel_library = zettelkasten.import_zk()
	# print(zettelkasten.timestamp())
	filepath = zettelkasten.file_path
	# zettelkasten.extract_filepath(filepath)
	# zettelkasten.export_zk(zettelkasten.extract_filepath(filepath), zettelkasten.zettel_library)

