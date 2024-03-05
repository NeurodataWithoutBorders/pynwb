.. _citing:

Citing PyNWB
============

BibTeX entry
------------

If you use PyNWB in your research, please use the following citation:

.. code-block:: bibtex

   @article {10.7554/eLife.78362,
        article_type = {journal},
        title = {{The Neurodata Without Borders ecosystem for neurophysiological data science}},
        author = {R\"ubel, Oliver and Tritt, Andrew and Ly, Ryan and Dichter, Benjamin K. and
                 Ghosh, Satrajit and Niu, Lawrence and Baker, Pamela and Soltesz, Ivan and
                 Ng, Lydia and Svoboda, Karel and Frank, Loren and Bouchard, Kristofer E.},
        editor = {Colgin, Laura L and Jadhav, Shantanu P},
        volume = {11{,
        year = {2022},
        month = {oct},
        pub_date = {2022-10-04},
        pages = {e78362},
        citation = {eLife 2022;11:e78362},
        doi = {10.7554/eLife.78362},
        url = {https://doi.org/10.7554/eLife.78362},
        keywords = {Neurophysiology, data ecosystem, data language, data standard, FAIR data, archive},
        journal = {eLife},
        issn = {2050-084X},
        publisher = {eLife Sciences Publications, Ltd},
  }


Using RRID
----------

* ResourceID: `SCR_017452 <https://scicrunch.org/resolver/SCR_017452>`_
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
