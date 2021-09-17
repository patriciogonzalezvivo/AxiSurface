install:
	pip3 install -r requirements.txt
	python3 setup.py install

install_blender_osx:
	rm -rf /Applications/Blender/blender.app/Contents/Resources/2.80/python/lib/python3.7/site-packages/AxiSurface*
	#/Applications/Blender/blender.app/Contents/Resources/2.80/python/bin/./python3.7m -m pip install -r requirements.txt --user
	/Applications/Blender/blender.app/Contents/Resources/2.80/python/bin/./python3.7m -m setup.py install 

clean:
	rm -rf build
	rm AxiSurface/*.pyc