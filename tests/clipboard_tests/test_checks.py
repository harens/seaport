#!/usr/bin/env python3

# Copyright (c) 2021, harens
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of seaport nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# See https://alexmarandon.com/articles/python_mock_gotchas/


from seaport._clipboard.checks import user_path


def test_user_path(fake_process) -> None:

    # Port prefix
    fake_process.register_subprocess(
        ["/usr/bin/which", "port"], stdout=["/opt/local/bin/port\n"], occurrences=5
    )

    assert user_path(True) == "/opt/local/bin"

    # Default prefix (first party tools)
    assert user_path() == "/usr/bin"

    # Third party tool prefixes

    # If installed by MacPorts
    fake_process.register_subprocess(
        ["/usr/bin/which", "seaport"], stdout=["/opt/local/bin/seaport\n"]
    )

    assert user_path(False, True) == "/opt/local/bin"

    # If installed by Homebrew

    fake_process.register_subprocess(
        ["/usr/bin/which", "seaport"], stdout=["/usr/local/bin/seaport\n"]
    )

    assert user_path(False, True) == "/usr/local/bin"

    # Poetry example (should default to MacPorts)

    fake_process.register_subprocess(
        ["/usr/bin/which", "seaport"],
        stdout=[
            "~/Library/Caches/pypoetry/virtualenvs/seaport-kpP_O3aU-py3.8/bin/seaport\n"
        ],
    )

    assert user_path(False, True) == "/opt/local/bin"
