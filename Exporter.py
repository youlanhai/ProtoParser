# -*- coding: utf-8 -*-
import os
import shutil
from Cheetah.Template import Template

import ppconfig
import generators
from cores import PCodes
from cores.PParser import PParser


class Exporter(object):
	
	def run(self, option):
		self.option = option

		outputPath = ppconfig.OUTPUT_PATH
		inputPath = ppconfig.INPUT_PATH

		if os.path.exists(outputPath):
			if option.force:
				shutil.rmtree(outputPath)
				os.mkdir(outputPath)
		else:
			os.mkdir(outputPath)

		self.module = PCodes.Module()
		self.parseInPath(inputPath)

		namespace = {
			"NAME" : os.path.basename(inputPath),
			"SOURCE_FILE" : inputPath,
			"OUTPUT_PATH" : outputPath,
		}
		self.generateCode(ppconfig.PROJECT_GENERATORS, self.module, namespace)

	def parseInPath(self, inputPath):
		self.module.searchPath.append(inputPath)

		files = os.listdir(inputPath)
		for fname in files:
			name, ext = os.path.splitext(fname)
			if ext != ".proto": continue

			srcFullPath = os.path.join(inputPath, fname)
			self.parseFile(name, srcFullPath, ppconfig.OUTPUT_PATH)

		return

	def parseFile(self, name, srcPath, outputPath):
		fileDescriptor = self.module.files.get(srcPath)
		if fileDescriptor is None:
			pa = PParser(self.module, srcPath)
			pa.parse()
			fileDescriptor = pa.fd

		namespace = {
			"NAME" : name,
			"SOURCE_FILE" : srcPath,
			"OUTPUT_PATH" : outputPath,
		}

		self.generateCode(ppconfig.CODE_GENERATORS, fileDescriptor, namespace)
		return True

	def generateCode(self, generatorInfos, code, namespace):
		for generatorInfo in generatorInfos:
			cls = getattr(generators, generatorInfo["class"])
			generator = cls(generatorInfo, self)

			dstPath = generatorInfo["output"]
			dstPath = str(Template(dstPath, searchList = [namespace, ]))
			generator.generate(namespace["NAME"], dstPath, code)

		return
