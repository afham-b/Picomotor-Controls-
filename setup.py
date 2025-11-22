from distutils.core import setup, Extension

asicamera_module = Extension(
    '_asicamera',
    sources=['asicamera_wrap.cxx'],
    include_dirs=['.'],
    library_dirs=['.'],
    libraries=['ASICamera2'],
    extra_compile_args=['-DWIN64'],
)

setup(
    name='asicamera',
    version='0.1',
    author='Your Name',
    description='Python bindings for ASI Camera SDK using SWIG',
    ext_modules=[asicamera_module],
    py_modules=['asicamera'],
)
