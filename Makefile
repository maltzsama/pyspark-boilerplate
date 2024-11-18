# Makefile

# Display available targets and their descriptions
help:
	@echo "Available targets:"
	@echo "  clean       - Remove all build, test, coverage, and Python artifacts"
	@echo "  clean-pyc   - Remove Python file artifacts"
	@echo "  clean-test  - Remove test and coverage artifacts"
	@echo "  lint        - Check code style"
	@echo "  test        - Run tests quickly with the default Python"
	@echo "  coverage    - Check code coverage quickly with the default Python"
	@echo "  build       - Package"
	@echo "  documentation - Generate documentation"
	@echo "  all         - Run default tasks"

# Default target
all: default

# Default tasks
default: clean dev_deps deps test lint build

# Virtual environment setup
.venv:
	if [ ! -e ".venv/bin/activate_this.py" ] ; then virtualenv --clear .venv ; fi

# Clean targets
clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr dist/
	rm -fr ./src/libs/

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/

# Dependency installation
deps: .venv
	. .venv/bin/activate && pip install --no-deps -r requirements.txt -t ./src/libs

dev_deps: .venv
	. .venv/bin/activate && pip install -r dev_requirements.txt

# Code style check
lint:
	. .venv/bin/activate && pylint -r n src/main.py src/shared src/jobs tests

# Test execution
test:
	. .venv/bin/activate && nosetests ./tests/* --config=.noserc

# ZIP file creation for distribution
create_zip:
	mkdir -p temp_directory
	cp -r ./src/jobs ./src/shared temp_directory
	cd temp_directory && zip -r ../dist/jobs.zip .
	rm -rf temp_directory

# Build tasks
build: clean deps
	mkdir ./dist
	cp ./src/main.py ./dist
	cd ./src && zip -x main.py -x \*libs\* -x \*venv\* -x .DS_Store \*idea\* -r  ../dist/jobs.zip .
	cd ./src/libs && zip -r ../../dist/libs.zip .

# Documentation generation
doc: doxygen

doxygen:
	@echo "Checking if Doxygen is installed..."
	@command -v doxygen > /dev/null || { \
		if [ "$(OS)" = "Windows_NT" ]; then \
			echo "Doxygen not found. Installing using chocolatey..."; \
			choco install doxygen; \
		else \
			if [ "$(shell uname)" = "Linux" ]; then \
				echo "Doxygen not found. Installing using apt..."; \
				sudo apt-get update && sudo apt-get install -y doxygen; \
			elif [ "$(shell uname)" = "Darwin" ]; then \
				echo "Doxygen not found. Installing using brew..."; \
				brew install doxygen; \
			else \
				echo "Unsupported operating system for automatic Doxygen installation."; \
				exit 1; \
			fi; \
		fi; \
	}
	@echo "Doxygen found. Generating documentation..."
	@doxygen Doxyfile


run:
	@echo "Running Spark job locally with spark-submit..."
	. .venv/bin/activate && \
	spark-submit \
		--master local[*] \
		--deploy-mode client \
		--conf "spark.sql.shuffle.partitions=4" \
		--conf "spark.executor.memory=2g" \
		--conf "spark.driver.memory=2g" \
		--py-files ./dist/libs.zip \
		./src/main.py --job $(job_name)