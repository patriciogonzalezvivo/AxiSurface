install:
	pip3 install -r requirements.txt
	python3 setup.py install

conda-install:
	conda env create -f environment.yml
	@echo "To activate the environment, run: conda activate Surface"
	@echo "Then install Surface with: pip install -e ."

conda-dev:
	conda env create -f environment.yml
	conda activate Surface && pip install -e .

clean:
	rm -rf build
	rm Surface/*.pyc

.PHONY: install conda-install conda-dev clean