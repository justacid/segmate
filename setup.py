import setuptools
import segmate


setuptools.setup(
    name="segmate",
    version=segmate.get_version(),
    python_requires=">=3.5",
    description="A tool to annotate segmentation data sets.",
    packages=setuptools.find_packages(),
    install_requires=[
        "PySide2 == 5.12.3",
        "scikit-image == 0.14.2",
        "imageio == 2.4.1",
        "natsort == 6.0.0"
    ],
    include_package_data=True,
    entry_points = {
        "gui_scripts": ["segmate = segmate.main:main"]
    }
)
