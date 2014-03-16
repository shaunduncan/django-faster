from setuptools import setup, find_packages

version = '0.0.1'

setup(name="django-faster",
      version=version,
      description=('Tools for doing faster/more efficient things for large django projects'),
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Web Environment',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Framework :: Django',
                   'Topic :: Software Development :: Libraries :: Python Modules'],
      keywords='django faster optimization improvements',
      author='Shaun Duncan',
      author_email='shaun.duncan@gmail.com',
      url='https://github.com/shaunduncan/django-faster',
      license='MIT',
      packages=find_packages(),
)
