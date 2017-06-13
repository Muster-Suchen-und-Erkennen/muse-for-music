from setuptools import setup

setup(
    name='muse_for_music',
    packages=['muse_for_music'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_sqlalchemy',
        'flask_webpack',
        'flask_jwt_extended',
        'flask_bcrypt',
        'flask_cors'
    ],
)
