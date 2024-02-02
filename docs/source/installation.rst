=========================
Installation
=========================


We define here two types of installation:

- `Installation for standard users`_ : for users who want to process data.

- `Installation for contributors`_: for contributors who want to enrich the project (eg. add a new reader).

We recommend users and contributors to first set up a `Virtual Environment <#virtual_environment>`_ where to install pycolorbar.


.. _virtual_environment:

Virtual Environment Creation
===============================

While not mandatory, utilizing a virtual environment when installing pycolorbar is recommended.

Using a virtual environment for installing packages provides isolation of dependencies,
easier package management, easier maintenance, improved security, and improved development workflow.

Here below we provide two options to set up a virtual environment,
using `venv <https://docs.python.org/3/library/venv.html>`__
or `conda <https://docs.conda.io/en/latest/>`__ (recommended).

**With conda:**

* Install `miniconda <https://docs.conda.io/en/latest/miniconda.html>`__
  or `anaconda <https://docs.anaconda.com/anaconda/install/>`__
  if you don't have it already installed.

* Create the `pycolorbar-py311` (or any other custom name) conda environment:

.. code-block:: bash

	conda create --name pycolorbar-py311 python=3.11 --no-default-packages

* Activate the `pycolorbar-py311` conda environment:

.. code-block:: bash

	conda activate pycolorbar-py311


**With venv:**

* Windows: Create a virtual environment with venv:

.. code-block:: bash

   python -m venv pycolorbar-pyXXX
   cd pycolorbar-pyXXX/Scripts
   activate


* Mac/Linux: Create a virtual environment with venv:

.. code-block:: bash

   virtualenv -p python3 pycolorbar-pyXXX
   source pycolorbar-pyXXX/bin/activate

Installation for standard users
==================================

The latest pycolorbar stable version is available
on the `Python Packaging Index (PyPI) <https://pypi.org/project/pycolorbar/>`__
and on the `conda-forge channel <https://anaconda.org/conda-forge/pycolorbar>`__.

Therefore you can either install the package with pip or conda (recommended).
Please install the package in the virtual environment you created before !

**With conda:**

.. code-block:: bash

   conda install -c conda-forge pycolorbar


.. note::
   In alternative to conda, if you are looking for a lightweight package manager you could use `micromamba <https://micromamba.readthedocs.io/en/latest/>`__.

**With pip:**

.. code-block:: bash

   pip install pycolorbar


Installation for contributors
================================

The latest pycolorbar version is available on the GitHub repository `pycolorbar <https://github.com/ghiggi/pycolorbar>`_.
You can install the package in editable mode, so that you can modify the code and see the changes immediately.
Here below we provide the steps to install the package in editable mode.

Clone the repository from GitHub
......................................

According to the `contributors guidelines <https://pycolorbar.readthedocs.io/en/latest/contributors_guidelines.html>`__,
you should first
`create a fork into your personal GitHub account <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo>__`.

Then create a local copy of the repository you forked with:

.. code-block:: bash

    git clone https://github.com/<your-account>/pycolorbar.git
    cd pycolorbar

Create the development environment
......................................

We recommend to create a dedicated conda environment for development purposes.
You can create a conda environment (i.e. with python 3.11) with:

.. code-block:: bash

	conda create --name pycolorbar-dev-py311 python=3.11 --no-default-packages
	conda activate pycolorbar-dev-py311

Install the pycolorbar package dependencies
............................................

.. code-block:: bash

	conda install --only-deps pycolorbar


Install the pycolorbar package in editable mode
................................................

Install the pycolorbar package in editable mode by executing the following command in the pycolorbar repository's root:

.. code-block:: bash

	pip install -e .


Install pre-commit code quality checks
..............................................

Install the pre-commit hook by executing the following command in the pycolorbar repository's root:

.. code-block:: bash

   pip install pre-commit
   pre-commit install


The pre-commit hooks are scripts executed automatically in every commit
to identify simple code quality issues. When an issue is identified
(the pre-commit script exits with non-zero status), the hook aborts the
commit and prints the error. Currently, pycolorbar tests that the
code to be committed complies with `black's  <https://github.com/psf/black>`__ format style
and the `ruff <https://github.com/charliermarsh/ruff>`__ linter.

In case that the commit is aborted, you only need to run `black` and `ruff` through your code.
This can be done by running ``black .`` and ``ruff check .`` or alternatively with ``pre-commit run --all-files``.
The latter is recommended since it indicates if the commit contained any formatting errors (that are automatically corrected).

.. note::
	The software version of pre-commit tools is defined into the `.pre-commit-config.yaml` file.


Run pycolorbar on Jupyter Notebooks
==================================

If you want to run pycolorbar on a `Jupyter Notebook <https://jupyter.org/>`__,
you have to take care to set up the IPython kernel environment where pycolorbar is installed.

For example, if your conda/virtual environment is named `pycolorbar-dev`, run:

.. code-block:: bash

    python -m ipykernel install --user --name=pycolorbar-dev

When you will use the Jupyter Notebook, by clicking on `Kernel` and then `Change Kernel`, you will be able to select the `pycolorbar-dev` kernel.
