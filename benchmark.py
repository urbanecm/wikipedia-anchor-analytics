#!/usr/bin/env python
#-*- coding: utf-8 -*-

import mwxml

dump = mwxml.Dump.from_file(open("cswiki-latest-pages-articles-multistream.xml"))

TARGET_PAGE = "Zakarpatsko"

for page in dump.pages:
	if page.title == TARGET_PAGE:
		print("Found!")
		break
