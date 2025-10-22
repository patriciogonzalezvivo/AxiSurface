install:
	pip3 install -r requirements.txt
	python3 setup.py install

conda-install:
	conda env create -f environment.yml
	@echo "To activate the environment, run: conda activate Berthe"
	@echo "Then install Berthe with: pip install -e ."

conda-dev:
	conda env create -f environment.yml
	conda activate Berthe && pip install -e .

clean:
	rm -rf build
	rm Berthe/*.pyc

.PHONY: install conda-install conda-dev clean