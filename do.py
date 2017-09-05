#-*- coding: utf-8 -*-
import os
import shutil
import imp

try:
	from Cheetah.Template import Template
except:
	print "Python module 'Cheetah' was required. use command `pip install Cheetah` to install it."
	exit()

import ppconfig
import generators
from cores import codes
from cores.PParser import PParser
from argparse import ArgumentParser

def generate_code(generatorInfos, module, namespace):
	for generatorInfo in generatorInfos:
		cls = getattr(generators, generatorInfo["class"])
		generator = cls(generatorInfo)

		tpl = Template(generatorInfo["output"], searchList = [namespace, ])
		dstPath = str(tpl)
		generator.generate(namespace["NAME"], dstPath, module)

	return

def convert(name, srcPath, outputPath, module):
	fileDescriptor = module.files.get(srcPath)
	if fileDescriptor is None:
		pa = PParser(module, srcPath)
		pa.parse()
		fileDescriptor = pa.fd

	namespace = {
		"NAME" : name,
		"SOURCE_FILE" : srcPath,
		"OUTPUT_PATH" : outputPath,
	}

	generate_code(ppconfig.CODE_GENERATORS, fileDescriptor, namespace)
	return True

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

	inputPath = option.input_path
	outputPath = option.output if option.output else "output"

	if os.path.exists(outputPath):
		if option.force:
			shutil.rmtree(outputPath)
			os.mkdir(outputPath)
	else:
		os.mkdir(outputPath)

	module = codes.Module()
	module.searchPath = [inputPath]

	files = os.listdir(inputPath)
	for fname in files:
		name, ext = os.path.splitext(fname)
		if ext != ".proto": continue

		srcFullPath = os.path.join(inputPath, fname)
		convert(name, srcFullPath, outputPath, module)

	namespace = {
		"NAME" : os.path.basename(inputPath),
		"SOURCE_FILE" : inputPath,
		"OUTPUT_PATH" : outputPath,
	}
	generate_code(ppconfig.PROJECT_GENERATORS, module, namespace)

if __name__ == "__main__":
	main()
