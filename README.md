# AxiSurface

Simple Python 2/3 module to make line SVG images for plotting

## Install

* Make sure you have `pip` installed, if not do:

```bash
sudo easy_install pip
``` 

* Clone this repo:

```bash
git clone git@github.com:patriciogonzalezvivo/Lines.git
cd Lines
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

# MacOS Notes:

```
pip install opencv-python
pip install opencv-contrib-python

brew install vtk
brew install boost-python --build-from-source  
brew install qd --build-from-source  
brew install graphviz  
```



# Example 

```python
from AxiSurface import AxiSurface, text, circle, rect

paper = AxiSurface()
t = paper.child('test')

circle(t, center=(paper.width*0.5, paper.height*0.5), radius=paper.width*0.5 )
rect(t, center=(0,0), size=(paper.width, paper.height) )
text(t, text='hello world', center=(paper.width*0.5, paper.height*0.5) )

paper.toSVG('test.svg')
```

# Acknowledgement

Special thanks to:

 * [Evil Mad Scientist](https://www.evilmadscientist.com/) for the great Axidrawer and the Paths of the Hershey Fonts in (`hersheydata.py`)

 * [Paul Butler great](https://paulbutler.org/) for [Surface Projection tutorial](https://bitaesthetics.com/posts/surface-projection.html) and [PenKit]() https://github.com/paulgb/penkit/) both of witch I took some code in (`shading.py`).