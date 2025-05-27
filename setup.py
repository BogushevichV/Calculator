from distutils.core import setup
from Cython.Build import cythonize
from setuptools import Extension

extensions = [
    Extension(
        "sound_controller",
        ["sound_controller.pyx"],
        libraries=["winmm"],  # Для winsound
        extra_compile_args=["/O2"]  # Оптимизация для Windows
    )
]

setup(
    name="SoundController",
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': "3",
        'embedsignature': True
    })
)