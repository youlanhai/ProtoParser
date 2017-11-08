# -*- coding: utf-8 -*-
import os
import re
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

			keys = module.files.keys()
			keys.sort()
			for key in keys:
				fileDescriptor = module.files[key]
				fileName = os.path.splitext(fileDescriptor.fileName)[0]
				self.fileName = fileName
				self.moduleName = "_".join(re.split(r"\W+", fileName))
				self.writeFileCodes(fileDescriptor.codes)
			self.writeReturn(self.functions)

		return
