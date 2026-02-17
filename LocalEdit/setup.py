.
"""
Setup script for LocalEdit.
Allows installation via: pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='localedit',
    version='0.1.0',
    author='LocalEdit Contributors',
    author_email='',
    description='Simple, local, privacy-focused video editor',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/LocalEdit',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=[
        'moviepy>=1.0.3',
        'Pillow>=10.0.0',
        'PyQt5>=5.15.9',
        'pydub>=0.25.1',
        'numpy>=1.24.0',
        'imageio>=2.31.0',
        'imageio-ffmpeg>=0.4.9',
        'tqdm>=4.65.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.0',
            'black>=23.7.0',
            'flake8>=6.1.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'localedit=Src.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['locales/*.json', 'assets/**/*'],
    },
    project_urls={
        'Bug Reports': 'https://github.com/yourusername/LocalEdit/issues',
        'Source': 'https://github.com/yourusername/LocalEdit',
        'Documentation': 'https://github.com/yourusername/LocalEdit/tree/main/docs',
    },
)
