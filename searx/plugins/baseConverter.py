# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring, missing-class-docstring
from __future__ import annotations
import typing

import re
import string

from flask_babel import gettext

from searx.plugins import Plugin, PluginInfo
from searx.result_types import EngineResults

if typing.TYPE_CHECKING:
    from searx.search import SearchWithPlugins
    from searx.extended_types import SXNG_Request


def convert_base(number: string, from_base: int, to_base: int) -> str:
    """
    Converts a number from one base to another for bases from 2 to 64.

    Parameters:
        number (str): The number as a string to be converted.
        from_base (int): The base of the input number.
        to_base (int): The base to convert the number to.

    Returns:
        str: The converted number as a string.
    """
    if not (2 <= from_base <= 64 and 2 <= to_base <= 64):
        raise ValueError("Bases must be between 2 and 64 inclusive.")

    chars = string.digits + string.ascii_uppercase + string.ascii_lowercase + '+/'
    char_to_value = {char: idx for idx, char in enumerate(chars)}

    # Convert input number to decimal
    decimal_number = 0
    for digit in number:
        if digit not in char_to_value or char_to_value[digit] >= from_base:
            raise ValueError(f"Invalid digit '{
                             digit}' for base {from_base}")
        decimal_number = decimal_number * from_base + char_to_value[digit]

    # Convert decimal number to target base
    if decimal_number == 0:
        return '0'

    result = ''
    while decimal_number > 0:
        decimal_number, remainder = divmod(decimal_number, to_base)
        result = chars[remainder] + result

    return result


class SXNGPlugin(Plugin):
    """Plugin converts strings to different hash digests.  The results are
    displayed in area for the "answers".
    """

    id = "hash_plugin"
    default_on = True
    keywords = ["base"]

    def __init__(self):
        super().__init__()

        self.parser_re = re.compile(f"({'|'.join(self.keywords)}) (.*)", re.I)
        self.info = PluginInfo(
            id=self.id,
            name=gettext("Base Convert"),
            description=gettext(
                "Converts diffrent number bases into eachothere."),
            examples=["base 2 101"],
            preference_section="query",
        )

    def post_search(self, request: "SXNG_Request", search: "SearchWithPlugins") -> EngineResults:
        """Returns a result list only for the first page."""
        results = EngineResults()

        if search.search_query.pageno > 1:
            return results

        m = self.parser_re.match(search.search_query.query)
        if not m:
            # wrong query
            return results

        function, string = m.groups()

        # sets up a try for error catching
        try:
            data = str(string).split(" ")
            curBase = data.pop(0)
            number = data.pop(0)

            # Checks if there is a target output base
            if len(data) > 0:
                newBase = data.pop(0)
                answer = "Base " + curBase + ": " + number + \
                    " -> Base " + newBase + ": " + \
                    str(convert_base(number, int(curBase), int(newBase)))

            # If not target base it defualts to base 10
            else:
                answer = "Base " + curBase + ": " + number + \
                    " -> Base 10: " + \
                    str(convert_base(number, int(curBase), 10))

            results.add(results.types.Answer(answer=answer))

        # IndexErrors are created by having less then 2 numbers as args
        except IndexError:
            pass
        # ValueErrors are created by passing a non valid base number
        except ValueError:
            pass
        return results
