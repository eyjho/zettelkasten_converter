#!/usr/bin/env python
# coding: utf-8

'''
Docstring
'''
from zettelkasten_txt_to_csv import Zettelkasten

if __name__ == '__main__':
	zettelkasten = Zettelkasten(diagnostics = False)
	zettelkasten.library = zettelkasten.import_zk()
	print(len(zettelkasten.library))
	filepath = zettelkasten.file_path
	zettelkasten.export_zk(zettelkasten.extract_filepath(filepath), zettelkasten.library)