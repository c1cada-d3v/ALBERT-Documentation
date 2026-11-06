from setuptools import find_packages, setup
from glob import glob
from ament_index_python.packages import get_package_share_directory

package_name = 'esp32_comms'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
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
            'esp32_rpi = esp32_comms.esp32_rpi:main',
        ],
    },
)
