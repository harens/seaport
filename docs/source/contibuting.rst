Contributing
-------------

Thank you for reading this document! 🎉

- Issue Tracker: `<https://github.com/harens/seaport/issues>`_
- Source Code: `<https://github.com/harens/seaport>`_

Any changes, big or small, that you think can help improve this project are more than welcome.

As well as this, feel free to open an issue with any new suggestions or bug reports. Every contribution is appreciated.

🎪 Project structure
*********************

:code:`seaport` is divided into two main sections:

- Updating the portfile and copying it to the clipboard (`clipboard <https://github.com/harens/seaport/tree/master/seaport/_clipboard>`_)
- Sending the pull request (`pull_request <https://github.com/harens/seaport/tree/master/seaport/_pull_request>`_)

Directories within each of these sections contain docstrings in their :code:`__init__.py` to explain what their purpose is.
The same is true with the individual files.

The modules in both these folders are imported and used in their designated *"main"* file. For the clipboard section, it's :code:`_clipboard/clipboard.py`,
and for the PR section, it's :code:`_pull_request/pull_request.py`. This is what is run when the CLT is used.

The `Python API <https://seaport.readthedocs.io/en/latest/reference.html>`_ is located in `portfile.py <https://github.com/harens/seaport/blob/master/seaport/portfile.py>`_.

🏗 Setting up the project
**************************

First, clone the project and install all the dependencies. This also installs a `pre-commit hook <https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks>`_ to lint the code.

.. code-block:: console

    git clone https://github.com/harens/seaport
    cd seaport
    poetry install && poetry shell
    pre-commit install
    seaport --help

🚀 Commits
***********

As of v0.6.1, seaport uses `commitizen <https://commitizen-tools.github.io/commitizen/>`_ to help manage commits.

To make a commit, stage the relevant changes, and then run :code:`cz c`.

🚧 Removing trailing whitespace
================================

One of the git commit hooks might complain that a file has trailing whitespace. To remove it from a file, run the following
(`credit <https://stackoverflow.com/a/10711226>`_):

.. code-block:: console

    find . -iname FILE -type f -exec sed -i '' 's/[[:space:]]\{1,\}$//' {} \+

📚 Build the Docs
******************

The documentation can be found in :code:`docs/source`.

We can use `sphinx-autobuild <https://github.com/executablebooks/sphinx-autobuild>`_ to continuously rebuild the docs when changes are made.

.. code-block:: console

    sphinx-autobuild docs/source docs/_build/html

🧪 Testing
************

🏃 Running Tests
=================

The test scripts can be found in :code:`scripts/tests`. Please make sure all tests pass before sending a PR. Thank you :)

To run all the tests at once, run :code:`bash ./scripts/tests/test.sh` from the root directory. Don't copy/paste while running the tests,
and make sure you have nothing important in your clipboard.

📝 Writing Tests
=================

When writing tests, note that `doctests <https://docs.python.org/3/library/doctest.html>`_ **are preferred to test files.**
However, use test files if mocking is necessary or if it wouldn't make sense to add a certain test to the documentation (e.g. testing internal features).

When adding a test file, please name it according to the file it's testing and place it in a corresponding directory.
(e.g. :code:`_clipboard/additional.py` would correspond to :code:`clipboard_tests/test_additional.py`).
