import setuptools
import sys

# Avoid native import statements as we don't want to depend on the package being created yet.
def load_module(module_name, full_path):
    if sys.version_info < (3,5):
        import imp
        return imp.load_source(module_name, full_path)
    import importlib
    spec = importlib.util.spec_from_file_location(module_name, full_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
version = load_module("duflat.version", "duflat/version.py")

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()


setuptools.setup(
    name='duflat',
    packages=setuptools.find_packages(),
    install_requires=[
        'docopt',
    ],
    python_requires='>=3.4.0',
    version=version.__version__,
    description='Produces a flat summary of disc usage.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='DomNomNom and the RLBot Community',
    author_email='dominikschmid93@gmail.com',
    url='https://github.com/DomNomNom/duflat',
    keywords=[''],
    license='MIT License',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    entry_points={
        # Allow people to run `duflat` instead of `python -m duflat`
        'console_scripts': ['duflat = duflat.__main__:main']
    },
    package_data={
        'duflat': [
            'duflat/default_match_config.cfg',
            'duflat/website/additional_website_code/*',
        ]
    },
)
