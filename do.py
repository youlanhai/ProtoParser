#-*- coding: utf-8 -*-

import sys
import os
import shutil
import codes
from parser import Parser

MODULE_PATH = os.path.abspath(os.path.dirname(__file__))
OUTPUT_PATH = os.path.join(MODULE_PATH, "temp")
INPUT_PATH = os.path.join(MODULE_PATH, "test/messages")

USAGE = "python do.py [input_path] [output_path]"

def convert(name, srcPath, dstPath, module):
	fileDesc = module.files.get(srcPath)
	if fileDesc is None:
		pa = Parser(module, srcPath)
		pa.parse()
		fileDesc = pa.fd

	from generators.NormalGenerator import NormalGenerator
	from generators.ListGenerator import ListGenerator

	NormalGenerator("up").generate(name, dstPath + "_up.lua", fileDesc)
	NormalGenerator("dn").generate(name, dstPath + "_dn.lua", fileDesc)
	NormalGenerator("up", "LuaOnCall").generate(name, dstPath + "_up_on.lua", fileDesc)
	NormalGenerator("dn", "LuaOnCall").generate(name, dstPath + "_dn_on.lua", fileDesc)

	ListGenerator().generate(name, dstPath + "_list.lua", fileDesc)
	return True

def main():
	outputPath = OUTPUT_PATH
	inputPath = INPUT_PATH

	if len(sys.argv) > 1: inputPath = sys.argv[1]
	if len(sys.argv) > 2: outputPath = sys.argv[2]

	if os.path.exists(outputPath):
		shutil.rmtree(outputPath)

	os.mkdir(outputPath)

	module = codes.Module()
	module.searchPath = [inputPath]

	files = os.listdir(inputPath)
	for fname in files:
		name, ext = os.path.splitext(fname)
		if ext != ".proto": continue

		srcPath = os.path.join(inputPath, fname)
		dstPath = os.path.join(outputPath, name)
		print "generate:", fname
		convert(fname, srcPath, dstPath, module)

if __name__ == "__main__":
	main()
