# Copyright (c) 2025 Kevin Rzepka <kdev@posteo.com>
# SPDX-License-Identifier: MIT
# License-Filename: LICENSE
class DCSPylotDashInvalidInputException(Exception):

    def __init__(self, *args):
        super().__init__(*args)


class DCSPylotDashResourceNotFoundException(Exception):

    def __init__(self, *args):
        super().__init__(*args)
