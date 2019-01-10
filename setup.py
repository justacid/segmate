import setuptools
import segmate


setuptools.setup(
    name="Segmate",
    version=segmate.__version__,
    description="A tool to annotate segmentation data sets.",
    packages=setuptools.find_packages(),
    install_requires=[
        "PySide2==5.11.2",
        "scikit-image",
        "imageio",
        "QDarkStyle==2.6.5"
    ],
    include_package_data=True,
    entry_points = {
        "gui_scripts": ["segmate = segmate.main:main"]
    }
)
