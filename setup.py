from setuptools import setup

setup(
    name='snapshotalyzer',
    version='0.1',
    author='Yauheni Neshyn',
    author_email='Neshyn.Z@gmail.com',
    description="Snapshotalyzer is a tool to manage AWS EC2 snapshots",
    packages=['snapshotalyzer'],
    url='https://github.com/Ujin-n/aws_snapshotalyzer.git',
    install_requires=['click', 'boto3'],
    entry_points={
        'console_scripts': ['snapshotalyzer=snapshotalyzer.snapshotalyzer:cli',]
    }
)
