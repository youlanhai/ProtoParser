# -*- coding: utf-8 -*-
import os
from Cheetah.Template import Template
from .Generator import Generator

class PackageGenerator(Generator):
	''' 每个文件对应的包名
	'''

	def generate(self, inputPath, outputPath, module):
		packages = []
		for fname, fd in module.files.items():
			packageName = fd.packageName
			if packageName is None: continue

			name = os.path.splitext(os.path.basename(fname))[0]
			packages.append((name, packageName))

		packages.sort(key = lambda x : x[0])

		namespace = {"packages" : packages, "module" : module}

		fmt = self.template.TEMPLATE
		tpl = Template(fmt, searchList = [namespace, self])

		with open(outputPath, "w", newline="\n") as f:
			f.write(str(tpl))

		return
