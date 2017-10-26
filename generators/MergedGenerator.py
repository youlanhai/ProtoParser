# -*- coding: utf-8 -*-
import os
from Cheetah.Template import Template

from NormalGenerator import NormalGenerator

class MergedGenerator(NormalGenerator):
	''' 合并模式的代码生成器，针对整个模块，将结果合并输出到一个文件中
	'''

	def collectCodes(self, module):
		codes = []
		for fileDescriptor in module.files.itervalues():
			codes.extend(fileDescriptor.codes)
		return codes

	def generate(self, inputPath, outputPath, module):
		self.inputPath = inputPath
		self.functions = []

		with open(outputPath, "wb") as f:
			self.stream = f

			for fileDescriptor in module.files.itervalues():
				fileName = fileDescriptor.fileName
				self.moduleName = os.path.splitext(os.path.basename(fileName))[0]
				self.writeFileCodes(fileDescriptor.codes)
			self.writeReturn(self.functions)

		return
