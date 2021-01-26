🌊 seaport
==========

|ci-badge| |rtd-badge| |cov-badge|

A more mighty `port bump` for `MacPorts <https://www.macports.org>`_!

.. code-block::

    > seaport clip gping
    🌊 Starting seaport...
    👍 New version is 1.2.0-post
    🔻 Downloading from https://github.com/orf/gping/tarball/v1.2.0-post/gping-1.2.0-post.tar.gz
    🔎 Checksums:
    Old rmd160: 8b274132c8389ec560f213007368c7f521fdf682
    New rmd160: 4a614e35d4e1e496871ee2b270ba8836f84650c6
    Old sha256: 1879b37f811c09e43d3759ccd97d9c8b432f06c75a27025cfa09404abdeda8f5
    New sha256: 1008306e8293e7c59125de02e2baa6a17bc1c10de1daba2247bfc789eaf34ff5
    Old size: 853432
    New size: 853450
    ⏪️ Changing revision numbers
    No changes necessary
    📋 The contents of the portfile have been copied to your clipboard!

✨ Features
-----------

* **Automatically determines new version numbers and checksums** for MacPorts portfiles.
* **Copies the changes to your clipboard 📋**, and optionally **sends a PR to update them**.
* Contains **additional checking functionality**, such as running tests, linting and installing the updated program.
* `PEP 561 compatible <https://www.python.org/dev/peps/pep-0561>`_, with built in support for type checking.

To find out more, please read the `Documentation <http://seaport.rtfd.io/>`_.

Installation
------------

Naturally, MacPorts needs to already be installed for the tool to function.

Homebrew 🍺
***********

For those with both Homebrew and MacPorts installed, you can run the following:

.. code-block::

    brew install harens/tap/seaport

Binary bottles are provided for x86_64_linux, catalina and big_sur.

.. note::
    ⚠️ You can install the development version by running the following:

    .. code-block::

        brew install harens/tap/seaport --HEAD

PyPi 🐍
********

If you install seaport via `PyPi <https://pypi.org/project/seaport/>`_ and you want it to send PRs for you, please install `GitHub CLI <https://cli.github.com>`_.

.. code-block::

    pip3 install seaport

🔨 Contributing
---------------

- Issue Tracker: `<https://github.com/harens/seaport/issues>`_
- Source Code: `<https://github.com/harens/seaport>`_

Any change, big or small, that you think can help improve this project is more than welcome 🎉.

As well as this, feel free to open an issue with any new suggestions or bug reports. Every contribution is appreciated.

©️ License
----------

Similar to other MacPorts-based projects, seaport is licensed under the `BSD 3-Clause "New" or "Revised" License <https://github.com/harens/seaport/blob/master/LICENSE>`_.

📒 Notice of Non-Affiliation and Disclaimer
-------------------------------------------

This project is not affiliated, associated, authorized, endorsed by, or in any way officially connected with the MacPorts Project, or any of its subsidiaries or its affiliates. The official MacPorts Project website can be found at `<https://www.macports.org>`_.

The name MacPorts as well as related names, marks, emblems and images are registered trademarks of their respective owners.

.. |ci-badge| image:: https://img.shields.io/github/workflow/status/harens/seaport/Tests?logo=github&style=flat-square
   :target: https://github.com/harens/seaport/actions
   :alt: GitHub Workflow Status
.. |rtd-badge| image:: https://img.shields.io/readthedocs/seaport?logo=read%20the%20docs&style=flat-square
   :target: https://seaport.rtfd.io/
   :alt: Read the Docs
.. |cov-badge| image:: https://img.shields.io/codecov/c/github/harens/seaport?logo=codecov&style=flat-square
   :target: https://codecov.io/gh/harens/seaport
   :alt: Codecov
