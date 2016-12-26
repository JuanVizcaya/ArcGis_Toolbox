from time import sleep
try:
	from pip import main
	try:
		main(['install','--upgrade','pip'])
	except:
		pass
	for mod in ['xlrd','xlwt','xlutils','dbfpy','lxml','pptx']:
		lst = []
		try:
			status = main(['install',mod])
			if status == 0:
				lst.append('Se instaló correctamente el módulo {0}'.format(mod))
			else:
				lst.append('No se pudo instalar el módulo {0}'.format(mod))
		except:
			lst.append('No es posible instalar el módulo {0}'.format(mod))
	for inst in lst:
		print(lst)
except ImportError:
	print ('Este equipo no tiene pip, por lo tanto no es posible hacer instalar los módulos requeridos')
sleep(10)