How to contribute to NWB software and documents
===============================================

.. _sec-code-of-conduct:

Code of Conduct
---------------

This project and everyone participating in it is governed by our `code of conduct guidelines <https://github.com/NeurodataWithoutBorders/pynwb/blob/dev/.github/CODE_OF_CONDUCT.rst>`_. By participating, you are expected to uphold this code. Please report unacceptable behavior.

.. _sec-contribution-types:

Types of Contributions
----------------------

Did you find a bug? or Do you intend to add a new feature or change an existing one?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Identify the appropriate repository** for the change you are suggesting:

   * Use `nwb-schema <https://github.com/NeurodataWithoutBorders/nwb-schema/>`_ for any changes to the NWB format schema, schema language, storage, and other NWB related documents
   * Use `PyNWB <https://github.com/NeurodataWithoutBorders/pynwb>`_  for any changes regarding the PyNWB API and the corresponding documentation
   * Use `MatNWB <https://github.com/NeurodataWithoutBorders/matnwb>`_  for any changes regarding the MatNWB API and the corresponding documentation

* **Ensure the feature or change was not already reported** by searching on GitHub under `PyNWB Issues <https://github.com/NeurodataWithoutBorders/pynwb/issues>`_ and `nwb-schema issues <https://github.com/NeurodataWithoutBorders/nwb-schema/issues>`_, respectively .

* If you are unable to find an open issue addressing the problem then open a new issue on the respective repository. Be sure to include:

    * **brief and descriptive title**
    * **clear description of the problem you are trying to solve***. Describing the use case is often more important than proposing a specific solution. By describing the use case and problem you are trying to solve gives the development team and ultimately the NWB community a better understanding for the reasons of changes and enables others to suggest solutions.
    * **context** providing as much relevant information as possible and if available a **code sample** or an **executable test case** demonstrating the expected behavior and/or problem.

* Be sure to select the appropriate labels (see :ref:`sec-issue-labels`) for your tickets so that they can be processed accordingly.

* NWB is currently being developed primarily by staff at scientific research institutions and industry, most of which work on many different research projects. Please be patient, if our development team is not able to respond immediately to your issues. In particular issues that belong to later project milestones may not be reviewed or processed until work on that milestone begins.

Did you write a patch that fixes a bug or implements a new feature?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
See the ``Contributing Patches and Changes`` section below for details.

Do you have questions about NWB?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ask questions on our `Slack workspace <https://nwb-users.slack.com>`_ or sign up for our `NWB mailing list <http://visitor.r20.constantcontact.com/manage/optin?v=001nQUq2GTjwCjZxK_V2-6RLElLJO1HMVtoNLJ-wGyDCukZQZxu2AFJmNh6NS0_lGMsWc2w9hZpeNn74HuWdv5RtLX9qX0o0Hy1P0hOgMrkm2NoGAX3VoY25wx8HAtIZwredcCuM0nCUGodpvoaue3SzQ%3D%3D>`_ for updates.

Informal discussions between developers and users?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The https://nwb-users.slack.com slack is currently used mainly for informal discussions between developers and users.

.. _sec-contributing:

Contributing Patches and Changes
--------------------------------

The ``dev`` branches of `PyNWB <https://github.com/NeurodataWithoutBorders/pynwb>`_ and `nwb-schema <https://github.com/NeurodataWithoutBorders/nwb-schema/>`_, are protected; you cannot push to them directly. You must upload your changes by pushing a new branch, then submit your changes to the ``dev`` branch via a `Pull Request <https://help.github.com/articles/creating-a-pull-request>`_. This allows us to conduct automated testing of your contribution, and gives us a space for developers to discuss the contribution and request changes. If you decide to tackle an issue, please make yourself an assignee on the issue to communicate this to the team. Don't worry - this does not commit you to solving this issue. It just lets others know who they should talk to about it.

From your local copy directory, use the following commands.

If you have not already, you will need to clone the repo:

.. code-block:: bash

    $ git clone --recurse-submodules https://github.com/NeurodataWithoutBorders/pynwb.git

1) First create a new branch to work on

.. code-block:: bash

    $ git checkout -b <new_branch>

2) Make your changes.

3) We will automatically run tests to ensure that your contributions didn't break anything and that they follow our style guide. You can speed up the testing cycle by running these tests locally on your own computer using ``tox`` and ``flake8``.

4) Push your feature branch to origin (i.e. github)

.. code-block:: bash

    $ git push origin <new_branch>

5) Once you have tested and finalized your changes, create a pull request (PR) targeting ``dev`` as the base branch:

    * Ensure the PR description clearly describes the problem and solution.
    * Include the relevant issue number if applicable. TIP: Writing e.g. "fix #613" will automatically close issue #613 when this PR is merged.
    * Before submitting, please ensure that the code follows the standard coding style of the respective repository.
    * If you would like help with your contribution, or would like to communicate contributions that are not ready to merge, submit a PR where the title begins with "[WIP]."
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

Style Guides
------------

Git Commit Message Style Guide
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Use the present tense ("Add feature" not "Added feature")
* The first line should be short and descriptive.
* Additional details may be included in further paragraphs.
* If a commit fixes an issues, then include "Fix #X" where X is the number of the issue.
* Reference relevant issues and pull requests liberally after the first line.

Documentation Style Guide
^^^^^^^^^^^^^^^^^^^^^^^^^

All documentations is written in reStructuredText (RST) using Sphinx.

Did you fix whitespace, format code, or make a purely cosmetic patch in source code?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Source code changes that are purely cosmetic in nature and do not add anything substantial to the stability, functionality, or testability will generally not be accepted unless they have been approved beforehand. One of the main reasons is that there are a lot of hidden costs in addition to writing the code itself, and with the limited resources of the project, we need to optimize developer time. E.g,. someone needs to test and review PRs, backporting of bug fixes gets harder, it creates noise and pollutes the git repo and many other cost factors.

Format Specification Style Guide
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Coming soon**

Python Code Style Guide
^^^^^^^^^^^^^^^^^^^^^^^

Before you create a Pull Request, make sure you are following the PyNWB style guide.
To check whether your code conforms to the PyNWB style guide, simply run the ruff_ tool in the project's root
directory. ``ruff`` will also sort imports automatically and check against additional code style rules.

We also use ``ruff`` to sort python imports automatically and double-check that the codebase
conforms to PEP8 standards, while using the codespell_ tool to check spelling.

``ruff`` and ``codespell`` are installed when you follow the developer installation instructions. See
:ref:`install_developers`.

.. _ruff: https://beta.ruff.rs/docs/
.. _codespell: https://github.com/codespell-project/codespell

.. code::

   $ ruff check .
   $ codespell

Endorsement
-----------

Please don’t take the fact that you worked with an organization (e.g., during a hackathon or via GitHub) as an endorsement of your work or your organization. It is okay to say e.g., “We worked with XXXXX to advance science” but not e.g., “XXXXX supports our work on NWB”.”


License and Copyright
---------------------

See the `license <https://raw.githubusercontent.com/NeurodataWithoutBorders/pynwb/dev/license.txt>`_ files for details about the copyright and license.

As indicated in the PyNWB license: *“You are under no obligation whatsoever to provide any bug fixes, patches, or upgrades to the features, functionality or performance of the source code ("Enhancements") to anyone; however, if you choose to make your Enhancements available either publicly, or directly to Lawrence Berkeley National Laboratory, without imposing a separate written license agreement for such Enhancements, then you hereby grant the following license: a non-exclusive, royalty-free perpetual license to install, use, modify, prepare derivative works, incorporate into other computer software, distribute, and sublicense such enhancements or derivative works thereof, in binary and source code form.”*

Contributors to the NWB code base are expected to use a permissive, non-copyleft open source license. Typically 3-clause BSD is used, but any compatible license is allowed, the MIT and Apache 2.0 licenses being good alternative choices. The GPL and other copyleft licenses are not allowed due to the consternation it generates across many organizations.

Also, make sure that you are permitted to contribute code. Some organizations, even academic organizations, have agreements in place that discuss IP ownership in detail (i.e., address IP rights and ownership that you create while under the employ of the organization). These are typically signed documents that you looked at on your first day of work and then promptly forgot. We don’t want contributed code to be yanked later due to IP issues.
