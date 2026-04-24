import os
from glob import glob    # all files /launch*
from setuptools import find_packages, setup # findpackage->__init__ is where , setup->how to install this pac

package_name = 'helios_description'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),  # find_packages() says: “include all folders that contain __init__.py.”
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), glob('launch/*')),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='dev',
    maintainer_email='adityadevsingh16@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    
    extras_require={
        'test': ['pytest'],
    },

    entry_points={
        'console_scripts': [
            'twist_2_pwm = helios_description.twist_2_pwm:main',
            'diff_tf = helios_description.diff_tf:main',
            'fkenc = helios_description.fkenc:main',
        ],
    },
)
