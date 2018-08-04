How to contribute to NWB:N software and documents
=================================================

.. _sec-code-of-conduct:

Code of Conduct
---------------

This project and everyone participating in it is governed by our `code of conduct guidelines <https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/docs/CONTRIBUTING.rst>`_. By participating, you are expected to uphold this code. Please report unacceptable behavior.

.. _sec-contribution-types:

Types of Contributions
----------------------

Did you find a bug? or Do you intend to add a new feature or change an existing one?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Identify the appropriate repository** for the change you are suggesting:

    * Use `nwb_schema <https://github.com/NeurodataWithoutBorders/nwb-schema/>`_ for any changes to the NWB:N format schema, schema language, storage and other NWB:N related documents
    * Use `PyNWB <https://github.com/NeurodataWithoutBorders/pynwb>`_  for any changes regarding the PyNWB API and the corresponding documentation

* **Ensure the feature or change was not already reported** by searching on GitHub under `PyNWB Issues <https://github.com/NeurodataWithoutBorders/pynwb/issues>`_ and  `nwh-schema issues <https://github.com/NeurodataWithoutBorders/nwb-schema/issues>`_ , respectively .

* If you are unable to find an open issue addressing the problem then open a new issue on the respective repository. Be sure to include:

    * **brief and descriptive title**
    * **clear description of the problem you are trying to solve***. Describing the use case is often more important than proposing a specific solution. By describing the use case and problem you are trying to solve gives the development team and ultimately the NWB:N community a better understanding for the reasons of changes and enables others to suggest solutions.
    * **context** providing as much relevant information as possible and if available a **code sample** or an **executable test case** demonstrating the expected behavior and/or problem.

* Be sure to select the appropriate labels (see :ref:`sec-issue-labels`) for your tickets so that they can be processed accordingly.

* NWB:N is currently being developed primarily by staff at scientific research institutions and industry, most of which work on many different research projects. Please be patient, if our development team is not able to respond immediately to your issues. In particular issues that belong to later project milestones may not be reviewed or processed until work on that milestone begins.

Did you write a patch that fixes a bug or implements a new feature?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See the ``Contributing Patches and Changes`` section below for details.


Did you fix whitespace, format code, or make a purely cosmetic patch in source code?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Source code changes that are purely cosmetic in nature and do not add anything substantial to the stability, functionality, or testability will generally not be accepted unless they have been approved beforehand. One of the main reasons is that there are a lot of hidden costs in addition to writing the code itself, and with the limited resources of the project, we need to optimize developer time. E.g,. someone needs to test and review PRs, backporting of bug fixes gets harder, it creates noise and pollutes the git repo and many other cost factors.

Do you have questions about NWB:N?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Join the `NWB:N mailing list <http://visitor.r20.constantcontact.com/manage/optin?v=001nQUq2GTjwCjZxK_V2-6RLElLJO1HMVtoNLJ-wGyDCukZQZxu2AFJmNh6NS0_lGMsWc2w9hZpeNn74HuWdv5RtLX9qX0o0Hy1P0hOgMrkm2NoGAX3VoY25wx8HAtIZwredcCuM0nCUGodpvoaue3SzQ%3D%3D>`_ for updates or ask questions on our `google group <https://groups.google.com/forum/#!forum/neurodatawithoutborders>`_.


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

4) Once you have tested and finalized your changes, create a pull request targeting ``dev`` as the base branch:

    * Ensure the PR description clearly describes the problem and solution.
    * Include the relevant issue number if applicable.
    * Before submitting, please ensure that the code follows the standard coding style of the repsective repository.
    * **NOTE:** Contributed branches will be removed by the development team after the merge is complete and should, hence, not be used after the pull request is complete.


.. _sec-issue-labels:

Issue Labels, Projects, and Milestones
--------------------------------------

Labels
^^^^^^

Labels are used to describe the general scope of an issue, e.g., whether it describes a bug or feature request etc. Please review and select the appropriate labels for the respective Git repository:

    * `PyNWB issue labels  <https://github.com/NeurodataWithoutBorders/pynwb/labels>`_
    * `nwb-schema issue labels  <https://github.com/NeurodataWithoutBorders/nwb-schema/labels>`_

Milestones
^^^^^^^^^^

Milestones are used to define the scope and general timeline for issues. Please review and select the appropriate milestones for the respective Git repository:

    * `PyNWB milestones <https://github.com/NeurodataWithoutBorders/pynwb/milestones>`_
    * `nwb-schema milestones <https://github.com/NeurodataWithoutBorders/nwb-schema/milestones>`_

Projects
^^^^^^^^

Projects are currently used mainly on the NeurodataWithoutBorders organization level and are only accessible to members of the organization. Projects are used to plan and organize developments across repositories. We currently do not use projects on the individual repository level, although that might change in the future.

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

Python coding style is checked via ``flake8`` for automatic checking of PEP8 style during pull requets.

Endorsement
-----------

Please don’t take the fact that working with an organization (e.g., during a hackathon or via GitHub) as an endorsement of your work or your organization. It’s okay to say  e.g., “We worked with XXXXX to advance science” but not e.g., “XXXXX supports our work on NWB”.”

Licence and Copyright
=======================

See the `Readme <https://github.com/NeurodataWithoutBorders/pynwb#contributing>`_ and correspoding `licence <https://raw.githubusercontent.com/NeurodataWithoutBorders/pynwb/dev/license.txt>`_ files for details about the copyright and licence.

As indicated in the PyNWB license: *“You are under no obligation whatsoever to provide any bug fixes, patches, or upgrades to the features, functionality or performance of the source code ("Enhancements") to anyone; however, if you choose to make your Enhancements available either publicly, or directly to Lawrence Berkeley National Laboratory, without imposing a separate written license agreement for such Enhancements, then you hereby grant the following license: a non-exclusive, royalty-free perpetual license to install, use, modify, prepare derivative works, incorporate into other computer software, distribute, and sublicense such enhancements or derivative works thereof, in binary and source code form.”*

Contributors to the NWB code base are expected to use a permissive, non-copyleft open source license. Typically 3-clause BSD i used, but any compatible license is allowed, the MIT and Apache 2.0 licenses being good alternative choices. The GPL and other copyleft licenses are not allowed due to the consternation it generates across many organizations.

Also, make sure that you are permitted to contribute code. Some organizations, even academic organizations, have agreements in place that discuss IP ownership in detail (i.e., address IP rights and ownership that you create while under the employ of the organization). These are typically signed documents that you looked at on your first day of work and then promptly forgot. We don’t want contributed code to be yanked later due to IP issues.
