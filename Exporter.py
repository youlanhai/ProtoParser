# -*- coding: utf-8 -*-
import os
import shutil
from Cheetah.Template import Template

import ppconfig
import generators
from cores import PCodes
from cores.PParser import PParser

def create_folder(folder, recreate = False):
	if os.path.exists(folder):
		if recreate:
			shutil.rmtree(folder)
			os.mkdir(folder)
	else:
		os.mkdir(folder)

class Exporter(object):
	
	def run(self, option):
		self.option = option

		outputPath = ppconfig.OUTPUT_PATH
		inputPath = ppconfig.INPUT_PATH

		namespace = {
			"NAME" : os.path.basename(inputPath),
			"SOURCE_FILE" : inputPath,
			"OUTPUT_PATH" : outputPath,
		}
		configCachePath = str(Template(ppconfig.MESSAGE_CONFIG_CACHE_FILE, searchList = [namespace, ppconfig]))

		self.module = PCodes.Module()
		self.module.loadConfigCache(configCachePath)

		create_folder(outputPath, option.force)
		self.parseInPath(inputPath)

		self.generateCode(ppconfig.PROJECT_GENERATORS, self.module, namespace)
		self.module.saveConfigCache(configCachePath)

	def parseInPath(self, inputPath):
		inputPath = os.path.normpath(inputPath)
		self.module.searchPath.append(inputPath)

		splitPos = len(inputPath) + 1
		for root, dirs, files in os.walk(inputPath):
			for fname in files:
				name, ext = os.path.splitext(fname)
				if ext != ".proto": continue

				srcFullPath = os.path.join(root, fname)
				relativePath = os.path.join(root[splitPos:], fname)

				self.parseFile(relativePath, srcFullPath, ppconfig.OUTPUT_PATH)
		return

	def parseFile(self, fileName, fileFullPath, outputPath):
		fileName = fileName.replace('\\', '/')
		fileDescriptor = self.module.getFileDescriptor(fileName)
		if fileDescriptor is None:
			fileDescriptor = self.module.newFileDescriptor(fileName, fileFullPath)
			pa = PParser(self.module, fileDescriptor)
			pa.parse()

		namespace = {
			"NAME" : os.path.splitext(fileName)[0],
			"SOURCE_FILE" : fileFullPath,
			"OUTPUT_PATH" : outputPath,
		}

		self.generateCode(ppconfig.CODE_GENERATORS, fileDescriptor, namespace)
		return True

	def generateCode(self, generatorInfos, code, namespace):
		for generatorInfo in generatorInfos:
			className = generatorInfo["class"]
			cls = getattr(generators, className) if isinstance(className, str) else className

			generator = cls(generatorInfo, self)

			dstPath = generatorInfo["output"]
			dstPath = str(Template(dstPath, searchList = [namespace, ppconfig]))
			generator.generate(namespace["NAME"], dstPath, code)

		return
