.. _citing:

Citing PyNWB
============

BibTeX entry
------------

If you use PyNWB in your research, please use the following citation:

.. code-block:: bibtex

  @article {R{\"u}bel523035,
      author = {R{\"u}bel, Oliver and Tritt, Andrew and Dichter, Benjamin and Braun, Thomas and Cain, Nicholas and Clack, Nathan and Davidson, Thomas J. and Dougherty, Max and Fillion-Robin, Jean-Christophe and Graddis, Nile and Grauer, Michael and Kiggins, Justin T. and Niu, Lawrence and Ozturk, Doruk and Schroeder, William and Soltesz, Ivan and Sommer, Friedrich T. and Svoboda, Karel and Lydia, Ng and Frank, Loren M. and Bouchard, Kristofer},
      title = {NWB:N 2.0: An Accessible Data Standard for Neurophysiology},
      elocation-id = {523035},
      year = {2019},
      doi = {10.1101/523035},
      publisher = {Cold Spring Harbor Laboratory},
      abstract = {Neurodata Without Borders: Neurophysiology (NWB:N) is a data standard for neurophysiology, providing neuroscientists with a common standard to share, archive, use, and build common analysis tools for neurophysiology data. With NWB:N version 2.0 (NWB:N 2.0) we made significant advances towards creating a usable standard, software ecosystem, and vibrant community for standardizing neurophysiology data. In this manuscript we focus in particular on the NWB:N data standard schema and present advances towards creating an accessible data standard for neurophysiology.},
      URL = {https://www.biorxiv.org/content/early/2019/01/17/523035},
      eprint = {https://www.biorxiv.org/content/early/2019/01/17/523035.full.pdf},
      journal = {bioRxiv}

Using duecredit
-----------------

Citations can be generated using duecredit_. To install duecredit, run ``pip install duecredit``.

You can obtain a list of citations for your Python script, e.g., ``yourscript.py``, using:

.. code-block:: bash

   cd /path/to/your/module
   python -m duecredit yourscript.py

Alternatively, you can set the environment variable ``DUECREDIT_ENABLE=yes``

.. code-block:: bash

   DUECREDIT-ENABLE=yes python yourscript.py

Citations will be saved in a hidden file (``.duecredit.p``) in the current directory. You can then use the duecredit_
command line tool to export the citations to different formats. For example, you can display your citations in
BibTeX format using:

.. code-block:: bash

   duecredit summary --format=bibtex

For more information on using duecredit, please consult its `homepage <https://github.com/duecredit/duecredit>`_.

.. _duecredit: https://github.com/duecredit/duecredit
