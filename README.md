# AxiSurface

Python 2/3 module to make 100% vector line compositions and export them as SVG or G-Code files. Made and tested for AxiDrawer plotter and SnapMaker CNC

Special thanks to:

 * [Michael Fogleman](https://www.michaelfogleman.com/): for [Axi](https://github.com/fogleman/axi) witch mostly of the `Path.py` class is based on

 * [Paul Butler](https://paulbutler.org/) for [Surface Projection tutorial](https://bitaesthetics.com/posts/surface-projection.html) witch `Texture.py` is based on

 * [Mat Handy](https://github.com/mathandy): for [SVGPathTools](https://github.com/mathandy/svgpathtools/) witch `Arc.py` is based on

 * [Evil Mad Scientist](https://www.evilmadscientist.com/) for the great Axidrawer


![00](examples/elements.png)
![01](examples/polyline.png)
![02](examples/image.png)


## Install

* Make sure you have `pip` installed, if not do:

```bash
sudo easy_install pip
``` 

* Clone this repo:

```bash
git clone git@github.com:patriciogonzalezvivo/AxiSurface.git
cd AxiSurface
```

* Run the install script directly with `make install` or manually do:

```bash
pip install -r requirements.txt
python setup.py install
```

Or use the Makefile by:

```bash
make install
```