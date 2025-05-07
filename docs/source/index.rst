.. PyNWB documentation master file, created by
   sphinx-quickstart on Thu Nov 17 10:41:07 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

NWB for Python
==============

PyNWB is a Python package for working with NWB files. It provides a high-level API for
efficiently working with neurodata stored in the NWB format. If you are new to NWB
and would like to learn more, then please also visit the :nwb_overview:`NWB Overview <>`
website, which provides an entry point for researchers and developers interested in using NWB.

`Neurodata Without Borders (NWB) <https://www.nwb.org/>`_ is a project to develop a
unified data format for cellular-based neurophysiology data, focused on the
dynamics of groups of neurons measured under a large range of experimental
conditions.

The NWB team consists of neuroscientists and software developers
who recognize that adoption of a unified data format is an important step toward
breaking down the barriers to data sharing in neuroscience.

.. raw:: html

   <div class="assistant-container">
     <iframe class="assistant-iframe"></iframe>
   </div>
   <button class="assistant-toggle">Open Assistant</button>
   <script>
     document.addEventListener('DOMContentLoaded', function() {
       const toggle = document.querySelector('.assistant-toggle');
       const container = document.querySelector('.assistant-container');
       const iframe = document.querySelector('.assistant-iframe');
       let iframeLoaded = false;

       toggle.addEventListener('click', function() {
         const isShowing = container.classList.toggle('show');

         // Load iframe content only when first opened
         if (isShowing && !iframeLoaded) {
           iframe.src = 'https://magland.github.io/nwb-assistant/chat';
           iframeLoaded = true;
         }
       });
     });
   </script>

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   install_users
   tutorials/index
   overview_citing

.. toctree::
   :maxdepth: 2
   :caption: Resources

   validation
   export
   api_docs

.. toctree::
   :maxdepth: 2
   :caption: For Developers

   install_developers
   overview_software_architecture
   update_requirements
   software_process
   make_a_release
   testing/index
   make_a_tutorial

.. toctree::
   :maxdepth: 2
   :caption: Contributing

   contributing
   legal

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
