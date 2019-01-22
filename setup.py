import setuptools
import segmate


setuptools.setup(
    name="Segmate",
    version=segmate.__version__,
    description="A tool to annotate segmentation data sets.",
    packages=setuptools.find_packages(),
    install_requires=[
        "PySide2==5.12.0",
        "scikit-image==0.14.2",
        "imageio==2.4.1",
        "QDarkStyle==2.6.5"
    ],
    include_package_data=True,
    entry_points = {
        "gui_scripts": ["segmate = segmate.main:main"]
    }
)
