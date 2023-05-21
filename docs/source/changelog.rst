Changelog
**********

v0.10.0 (2023-05-21)
======================

⚡️ Features
------------
- The downloaded distfile used for determining checksums is cached so that MacPorts can use it for
  :code:`port install/test/etc`.
- :code:`port clean` is no longer run at the end. The user might want to keep the distfiles for further tests or
  builds, and can run :code:`port clean` themselves if required.
- :code:`--gh` flag added to the pr command. It allows users to explicitly set the path to GitHub CLI.
- The port name is now capitalised correctly regardless of what the user types in.
- Paths for various system commands (e.g. MacPorts, GitHub CLI, etc.) are cached.

v0.9.0 (2023-02-12)
=====================

🚨 BREAKING CHANGE
--------------------

- The :code:`len` method of the Port API has been removed.

⚡️ Features
------------

- Sped up the Port API by reducing the number of calls to the port command.
- Sudo no longer required if portfile is already writable or just linting.
- Added a :code:`repr` method to the Port API.

🎭 Behind the Scenes
---------------------

- :code:`typing_extensions` is now required for Python <3.9.
- Simplified checksum calculations.
- Checks that website starts with http.

v0.8.0 (2023-02-07)
=====================

⚡️ Features
------------

- Added compatibility with Python 3.11.

v0.7.1 (2022-09-23)
=====================

⚡️ Features
------------

- The shell autocomplete scripts have been updated to support Click 8.

🐛 Bugfixes
------------

- Fixed `PEP 585 deprecation warnings <https://github.com/beartype/beartype#pep-585-deprecations>`_ when attempting
  to use autocompletion.

v0.7.0 (2022-08-06)
===========================

🚨 BREAKING CHANGE
--------------------

- The :code:`careful` parameter of the Port API has been removed. This is now determined automatically.

⚡️ Features
------------

- The :code:`-s` flag has been dropped from during CLT installation.
    - If the port version is being bumped, binaries aren't available so the flag doesn't make a difference.
      The issue with :code:`-s` is that the deps are then built from source, wasting time.

🐛 Bugfixes
------------

- With the CLT, there were previously some scenarios where a port is
  completely up-to-date but the CLT would say it's up-to-date with an older version.

v0.6.1 (2022-08-03)
===========================

⚡️ Features
------------

- Compatible with all `supported Python versions <https://endoflife.date/python>`_ (3.7-3.10).

🎭 Behind the Scenes
---------------------

- **pep585_constants**: replace with beartype.typing.

🐛 Bugfixes
------------

- fixes :code:`--test` when a port has no subports.

v0.6.0 (2022-02-12)
===========================

⚡️ Features
------------

- Replaced the wait after installation with a prompt asking whether or not to uninstall the port. `#35 <https://github.com/harens/seaport/issues/35>`_

v0.5.0 (2021-03-23)
===========================

⚡️ Features
------------

- The beginnings of a Python API have been created. It has basic features such as portfile version numbers and livecheck.
- Added a new :code:`--write` flag, which writes the updated portfile contents to the original file (similar to how port bump works). `#20 <https://github.com/harens/seaport/issues/20>`_
- Added a :code:`--url` flag to manually set the url to download the new file from. This helps if seaport gets the url wrong.
- Speed boost by preferring :code:`port info --index` over :code:`port info`. This relies on the information cached in the port index. However, it isn't always accurate so seaport falls back to removing the index flag if required.

🐛 Bugfixes
------------

- Fixes an issue when sending a PR where the commits get messed up if not on the master branch at the beginning (such as `macports/macports-ports#9444 <https://github.com/macports/macports-ports/pull/9944>`_).

📚 Improved Documentation
---------------------------

- The `Python API <https://seaport.readthedocs.io/en/latest/reference.html>`_ has been documented with examples.
- A `contributing <https://seaport.readthedocs.io/en/latest/contributing.html>`_ page has been added.

🎭 Behind the Scenes
---------------------

- Improved `PEP 585 <https://www.python.org/dev/peps/pep-0585/>`_ compliance, with different type hints for different python versions.
- Test files are now fully type checked - with full use of `beartype <https://github.com/beartype/beartype>`_, `mypy <http://www.mypy-lang.org/>`_ and `pytype <https://google.github.io/pytype>`_ throughout the code base.
- Fixed an issue where the `API reference <https://seaport.readthedocs.io/en/latest/reference.html#>`_ and `CLT overview <https://seaport.readthedocs.io/en/latest/overview.html>`_ weren't rendered properly.

v0.4.1 (2021-01-26)
==========================

⚡️ Features
------------

- User alerted that the CLT version is used for PR template if Xcode isn't installed
- Basic GitHub Actions support has been added (updating contents and sending PR only)


🐛 Bugfixes
------------

- Fixed an issue where the contents are copied to the clipboard but seaport thinks otherwise


📚 Improved Documentation
---------------------------

- Docs created on RTD
- This changelog has been created
