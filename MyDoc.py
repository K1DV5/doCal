from shutil import rmtree
import sympy as sp
from sympy import Symbol
from sympy.physics.units import meter, second, kilogram, convert_to
import __main__
class document:
	'''contains (almost) all of the functionality for a LaTeX document'''
	def __init__(self):
		self.name = __main__.__file__.replace('.py', '')
		self.type = 'article'
		self.options = '11pt'
		self.preamble = ''
		self.content = ''
		self.file = 'tex'
		self.folder = 'RnD'
		self.dir = 'here'
	def __enter__(self):
		return self
	def append(self, content, whitespace = 2):
		self.content = self.content + '\n' * whitespace + content
	def chapter(self, title):
		self.append('\n\\chapter{' + title + '}', 1)
	def section(self, title):
		self.append('\n\\section{' + title + '}', 1)
	def subsection(self, title):
		self.append('\n\\subsection{' + title + '}', 1)
	def subsubsection(self, title):
		self.append('\n\\subsubsection{' + title + '}', 1)
	def equation(self, *eqns, inline: bool = False):
		if len(eqns) == 1:
			if inline == True:
				self.append(' $' + eqns[0] + '$ ', 1)
			else:
				self.append('\n\\begin{equation}\n' + eqns[0] + '\n\\end{equation}', 1)
		else:
			self.append('\n\\begin{align}\n\\begin{split}', 1)
			for eq in eqns:
				self.append(eq.replace('=', '&=') +'\\\\', 1)
			self.append('\\end{split}\n\\end{align}', 1)
	def aserar(self, eqn, intent = 'full', unit = [meter, second, kilogram]):
		def format_quantity(qty):
			'''returns a nicely latex formatted string of the quantity including the units (if any)'''
			try:
				return(str(round(float(qty), 3)))
			except:
				number = list(convert_to(qty, unit).evalf(5).as_coefficients_dict().values())[0]
				un = '\\mathrm{' + sp.latex(list(convert_to(qty.evalf(), unit).as_coefficients_dict().keys())[0]) + '}'
				abb = {'meter': 'm', 'second': 's'}
				fmtd = str(number) + '\\,' + un
				for full_form, short_form in abb.items(): fmtd = fmtd.replace(full_form, short_form)
				return fmtd
		lhand = eqn.split('=')[0].strip()
		simplified = sp.simplify(eqn.split('=')[1].strip())
		variable_main = '__main__.' + lhand
		free_symbols = list(simplified.atoms(Symbol))
		variables_list = [sp.latex(var) for var in free_symbols]
		values_list = [eval('__main__.' + str(var)) for var in free_symbols]
		values_dict = dict(zip(variables_list, values_list))
		expr_2_str = str(simplified)
		for var in free_symbols: expr_2_str = expr_2_str.replace(str(var), '__main__.'+str(var))
		exec(variable_main + '=' + expr_2_str)
		variable_lx = sp.latex(sp.simplify(lhand))
		expr_1_lx = sp.latex(simplified, mul_symbol = 'dot')
		expr_2_lx = sp.latex(simplified, mul_symbol = 'times')
		for var, val in values_dict.items(): expr_2_lx = expr_2_lx.replace(var, format_quantity(val))
		expr_3_lx = format_quantity(simplified.subs(dict(zip(free_symbols, values_list))))
		_tabs_ = len(variable_lx)//4
		if intent == 'define':
			self.equation (variable_lx + ' = ' + expr_3_lx, inline = True)
		elif intent == '2steps' or intent == '2step':
			self.equation (variable_lx + '\t= ' + expr_1_lx, _tabs_*'\t' + '\t= ' + expr_3_lx)
		else:
			self.equation (variable_lx + '\t= ' + expr_1_lx, _tabs_*'\t' + '\t= ' + expr_2_lx, _tabs_*'\t' + '\t= ' + expr_3_lx)
	def __exit__(self, *args):
		self.content = '\\documentclass[' + self.options + ']{' + self.type + '}\n\\usepackage{amsmath}' + self.preamble + '\n\\begin{document}' + self.content.replace('_{}', '') + '\n\n\\end{document}'
		if self.dir == 'here': directory = ''
		else: directory = 'C:/Users/Kidus III/Documents/LaTeX/' + self.folder + '/'
		with open(directory + self.name + '.tex', 'w') as file:
			file.write(self.content)
		rmtree('__pycache__', ignore_errors = True)
		if self.file != 'tex':
			from subprocess import run
			run(['pandoc', directory + self.name + '.tex', '-o', directory + self.name + '.' + self.file])