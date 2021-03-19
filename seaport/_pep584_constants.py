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

"""Constants to deal with type hints in different python versions."""

# Credit to beartype organisation
# See https://github.com/beartype/beartype/blob/main/beartype/_util/hint/data/pep/utilhintdatapepsign.py

import sys
from typing import Any

# Deals with typing module being depreciated in PEP 585
# Credit to https://stackoverflow.com/a/62900998/10763533
# Credit to https://github.com/beartype/beartype/issues/30#issuecomment-792490864
PYTHON_AT_LEAST_3_9 = sys.version_info >= (3, 9)

# Use typing module below python 3.9
# Initialised first with Any to make mypy happy
LIST_TYPE: Any = None
TUPLE_TYPE: Any = None

if PYTHON_AT_LEAST_3_9:
    LIST_TYPE = list
    TUPLE_TYPE = tuple
else:
    from typing import List, Tuple

    LIST_TYPE = List
    TUPLE_TYPE = Tuple
