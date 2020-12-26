# -*- coding: utf-8 -*-
import os
import re
from Cheetah.Template import Template

from .NormalGenerator import NormalGenerator

class MergedGenerator(NormalGenerator):
	''' 合并模式的代码生成器，针对整个模块，将结果合并输出到一个文件中
	'''

	def collectCodes(self, module):
		codes = []
		for fileDescriptor in module.files.values():
			codes.extend(fileDescriptor.codes)
		return codes

	def generate(self, inputPath, outputPath, module):
		self.inputPath = inputPath

		with open(outputPath, "wb") as f:
			self.stream = f

			self.writeHeader()
			keys = list(module.files.keys())
			keys.sort()
			for key in keys:
				self.fileDescriptor = module.files[key]
				self.fileName = os.path.splitext(self.fileDescriptor.fileName)[0]
				self.moduleName = "_".join(re.split(r"\W+", self.fileName))
				self.writeFileCodes(self.fileDescriptor.codes)
				
			self.writeReturn()
		return
