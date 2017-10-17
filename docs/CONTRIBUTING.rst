How to contribute to NWB:N software and documents
=================================================

.. _sec-code-of-conduct:

Code of Conduct
---------------

This project and everyone participating in it is governed by our `code of conduct guidelines <docs/CODE_OF_CONDUCT.rst>`_. By participating, you are expected to uphold this code. Please report unacceptable behavior.

.. _sec-contribution-types:

Types of Contributions
----------------------

Did you find a bug? or Do you intend to add a new feature or change an existing one?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Identify the approbritate repository** for the change you are suggesting:

    * Use `nwb_schema <https://github.com/NeurodataWithoutBorders/nwb-schema/>`_ for any changes to the NWB:N format schema, schema language, storage and other NWB:N related documents
    * Use `PyNWB <https://github.com/NeurodataWithoutBorders/pynwb>`_  for any changes regarding the PyNWB API and the corresponding documentation

* **Ensure the feature or change was not already reported** by searching on GitHub under `PyNWB Issues <https://github.com/NeurodataWithoutBorders/pynwb/issues>`_ and  `nwh-schema issues <https://github.com/NeurodataWithoutBorders/nwb-schema/issues>`_ , respectively .

* If you are unable to find an open issue addressing the problem then open a new issue on the respective repository. Be sure to include:

    * **brief and descriptive title**
    * **clear description of the problem you are trying to solve***. Describing the use case is often more important than proposing a specific solution. By describing the use case and problem you are trying to solve gives the development team and ultimately the NWB:N community a better understanding for the reasons of changes and enables other to suggest solutions.
    * **context** providing as much relevant information as possible and if available a **code sample** or an **executable test case** demonstrating the expected behavior and/or problem.

* Be sure to select the approbritate labels (see :ref:`sec-issue-labels`) for your tickets so that they can be processed accordingly.

* NWB:N is currently being developed primarily by staff at scientific research institutions and industry, most of which work on many different research projects. Please be patient, if our development team may not be able to respond immediately to your issues. In particular issues that belong to later project milestones may not be reviewed or processed until work on that milestone begins.

Did you write a patch that fixes a bug or implements a new feature?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See the ``Contributing Patches and Changes`` section below for details.


Did you fix whitespace, format code, or make a purely cosmetic patch in source code?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Source code changes that are purely cosmetic in nature and do not add anything substantial to the stability, functionality, or testability will generally not be accepted unless they have been approved beforehand. One of the main reasons is that there are a lot of hidden cost in addition to writing the code itself, and with the limited resources of the project, we need to optimize developer time. E.g,. someone needs to test and review PRs, backporting of bug fixes gets harder, it creates noise and pollutes the git repo and many other cost factors.

Do you have questions about NWB:N?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Coming Soon (Google Group?)

Informal discussions between developers, users, and team?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The https://nwb-users.slack.com slack is currently used  mainly for internal discussions between developers, users, and teams.


.. _sec-contributing:

Contributing Patches and Changes
--------------------------------

To contribute to the `PyNWB <https://github.com/NeurodataWithoutBorders/pynwb>`_ and `nwb_schema <https://github.com/NeurodataWithoutBorders/nwb-schema/>`_, you must submit your changes to the ``dev`` branch via a `Pull Request <https://help.github.com/articles/creating-a-pull-request>`_.

From your local copy directory, use the following commands.

1) First create a new branch to work on

.. code-block:: bash

    $ git checkout -b <new_branch>

2) Make your changes.

3) Push your feature branch to origin (i.e. github)

.. code-block:: bash

    $ git push origin <new_branch>

4) Once you have tested and finalized your changes, create a pull request to dev:

    * Ensure the PR description clearly describes the problem and solution.
    * Include the relevant issue number if applicable.
    * Before submitting, please ensure that the code follows the standard coding style of the repsective repository.
    * **NOTE:** Contributed branches will be removed by the development team after the merge is complete and should, hence, not be used after the pull request is complete.


.. _sec-issue-labels:

Issue Labels, Projects, and Milestones
--------------------------------------

Labels
^^^^^^

Labels are used to describe the general scope of an issues, e.g., whether it describes a bug or feature request etc. Please review and select the approbritate labels for the respective Git repository:

    * `PyNWB issue labels  <https://github.com/NeurodataWithoutBorders/pynwb/labels>`_
    * `nwb-schema issue labels  <https://github.com/NeurodataWithoutBorders/nwb-schema/labels>`_

Milestones
^^^^^^^^^^

Milestones are used to define the scope and general timeline for issues. Please review and select the approbritate milestones for the respective Git repository:

    * `PyNWB milestones <https://github.com/NeurodataWithoutBorders/pynwb/milestones>`_
    * `nwb-schema milestones <https://github.com/NeurodataWithoutBorders/nwb-schema/milestones>`_

Projects
^^^^^^^^

Projects are currently used mainly on the NeurodataWithoutBorders organization level and are only accessible to members of organization. Projects are use to plan and organize developments across repositories. We currently do not use projects on the individual repository level, although that might change in the future.

.. _sec-styleguides:

Styleguides
-----------

Git Commit Message Styleguide
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Use the present tense ("Add feature" not "Added feature")
* The first should be short and descriptive.
* Additional details may be included in further paragraphs.
* If a commit fixes an issues, then include "Fix #X" where X is the number of the issue.
* Reference relevant issues and pull requests liberally after the first line.

Documentation Styleguide
^^^^^^^^^^^^^^^^^^^^^^^^

All documentations is written in reStrcuturedText (RST) using Sphinx.

Format Specification Styleguide
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Coming soon**

Python Code Styleguide
^^^^^^^^^^^^^^^^^^^^^^

**Coming soon**



Licence and Copyright
=======================

See the `Readme <../Readme.rst>`_ and correspoding `licence <../licence.txt>`_ files for details about the copyright and licence.



