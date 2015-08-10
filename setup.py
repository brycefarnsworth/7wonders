try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup
	
config = {
	'description': '7 Wonders',
	'author': 'Bryce Farnsworth',
	'url': 'URL to get it at.',
	'download_url': 'Where to download it.',
	'author_email': 'bryce.farnsworth@gmail.com',
	'version': '0.1',
	'install_requires': ['nose'],
	'packages': ['7wonders'],
	'scripts': [],
	'name': '7wonders'
}

setup(**config)