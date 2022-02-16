.. _citing:

Citing PyNWB
============

BibTeX entry
------------

If you use PyNWB in your research, please use the following citation:

.. code-block:: bibtex

    @article {R{\"u}bel2021.03.13.435173,
     author = {R{\"u}bel, Oliver and Tritt, Andrew and Ly, Ryan and Dichter, Benjamin K. and Ghosh, Satrajit and Niu, Lawrence and Soltesz, Ivan and Svoboda, Karel and Frank, Loren and Bouchard, Kristofer E.},
     title = {The Neurodata Without Borders ecosystem for neurophysiological data science},
     elocation-id = {2021.03.13.435173},
     year = {2021},
     doi = {10.1101/2021.03.13.435173},
     publisher = {Cold Spring Harbor Laboratory},
     abstract = {The neurophysiology of cells and tissues are monitored electrophysiologically and optically in diverse experiments and species, ranging from flies to humans. Understanding the brain requires integration of data across this diversity, and thus these data must be findable, accessible, interoperable, and reusable (FAIR). This requires a standard language for data and metadata that can coevolve with neuroscience. We describe design and implementation principles for a language for neurophysiology data. Our software (Neurodata Without Borders, NWB) defines and modularizes the interdependent, yet separable, components of a data language. We demonstrate NWB{\textquoteright}s impact through unified description of neurophysiology data across diverse modalities and species. NWB exists in an ecosystem which includes data management, analysis, visualization, and archive tools. Thus, the NWB data language enables reproduction, interchange, and reuse of diverse neurophysiology data. More broadly, the design principles of NWB are generally applicable to enhance discovery across biology through data FAIRness.Competing Interest StatementThe authors have declared no competing interest.},
     URL = {https://www.biorxiv.org/content/early/2021/03/15/2021.03.13.435173},
     eprint = {https://www.biorxiv.org/content/early/2021/03/15/2021.03.13.435173.full.pdf},
     journal = {bioRxiv}
    }

Using RRID
----------

* ResourceID: `SCR_017452 <https://scicrunch.org/browse/resources/SCR_017452>`_
* Proper Citation: **(PyNWB, RRID:SCR_017452)**


Using duecredit
---------------

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
