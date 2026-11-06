from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'facial_exp'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        (os.path.join('share', package_name, 'sprite_folder'), glob('facial_exp/sprite_folder/*.png')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='c1c@d@',
    maintainer_email='engr.pfister@proton.me',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'expressions = facial_exp.expressions:main',
        ],
    },
)
