Maintainer Notes
--------------------

🥾 Bumping Version Number
****************************

Have you updated the :code:`contributing.rst` file by cross-referencing with :code:`cz changelog`?

If so, run :code:`cz bump -s --increment LEVEL`, where LEVEL could be major, minor or patch.

Deploy to PyPi by running :code:`poetry build` and :code:`poetry publish`. Also update the Homebrew formula.

📆 Updating Copyright Year
****************************

As an example, running the below code block from the project root directory will update the copyright year from 2021 to 2022.

Credit to `these <https://stackoverflow.com/a/19770395>`_ `two <https://stackoverflow.com/a/22385837/10763533>`_ suggestions.

.. code-block:: console

    export LC_CTYPE=C
    export LANG=C
    grep -rl 'Copyright (c) 2022' . | xargs sed -i "" -e 's/Copyright (c) 2022/Copyright (c) 2023/g'
