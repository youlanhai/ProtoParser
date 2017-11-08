#-*- coding: utf-8 -*-
import os
import imp
from argparse import ArgumentParser
from cores.PLexer import ProtoException

try:
	import Cheetah
except:
	print "Python module 'Cheetah' was required. use command `pip install Cheetah` to install it."
	exit()

import ppconfig
from Exporter import Exporter

def parse_config(path):
	path = os.path.abspath(path)
	print "load configure file", path

	if not os.path.exists(path):
		raise RuntimeError, "the configure file '%s' doesn't exist" % path

	cfg = imp.load_source("custom_configure", path)
	for k, v in cfg.__dict__.iteritems():
		if k.startswith('_'): continue

		setattr(ppconfig, k, v)

	ppconfig.custom_init()
	return

def main():
	parser = ArgumentParser(description="Protobuf Parser")
	parser.add_argument("-output", help="output directory. default is 'output', under current path")
	parser.add_argument("-f", "--force", action="store_true", help="this will remove all old files.")
	parser.add_argument("-config", help="the configure file for code generator. see ppconfig.py")
	parser.add_argument("input_path", help="input proto directory. only *.proto files will be processed.")

	option = parser.parse_args()

	if option.config:
		parse_config(option.config)

	ppconfig.INPUT_PATH = option.input_path
	ppconfig.OUTPUT_PATH = option.output if option.output else "output"

	exporter = Exporter()
	try:
		exporter.run(option)
	except ProtoException, msg:
		print "\n**%s\n" % msg

if __name__ == "__main__":
	main()
