# -*- coding: utf-8 -*-
import os
from Cheetah.Template import Template

from NormalGenerator import NormalGenerator

class MergedGenerator(NormalGenerator):
	''' 合并模式的代码生成器，针对整个模块，将结果合并输出到一个文件中
	'''

	def collectCodes(self, module):
		codes = []
		for fileDescriptor in module.files:
			codes.extend(fileDescriptor.codes)
		return codes

	def generate(self, inputPath, outputPath, module):
		codes = self.exporter.get("codes")
		if codes is None:
			codes = self.collectCodes(module)
			# 将代码缓存起来，方便再次生成时使用
			self.exporter.codes = codes

		self.inputPath = inputPath
		self.moduleName = inputPath
		self.functions = []

		with open(outputPath, "wb") as f:
			self.stream = f

			self.writeFileCodes(codes)
			self.writeReturn(self.functions)

		return
