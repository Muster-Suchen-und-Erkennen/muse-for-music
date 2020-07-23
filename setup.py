from setuptools import setup

setup(
    name="muse_for_music",
    packages=["muse_for_music"],
    include_package_data=True,
    python_requires=">=3.5",
    install_requires=[
        "invoke>=1.4.1",
        "flask~=1.1.2",
        "flask-restx==0.2.0",
        "flask-sqlalchemy~=2.4.1",
        "flask-migrate~=2.5.3",
        "flask-webpack==0.1.0",
        "flask-static-digest~=0.1.3",
        "flask-cors~=3.0.8",
        "flask-jwt-extended~=3.24.1",
        "flask-bcrypt~=0.7.1",
    ],
    dependency_links=[],
)
