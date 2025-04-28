# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring
from __future__ import annotations

from functools import reduce
from operator import mul
import random

import babel
import babel.numbers
from flask_babel import gettext

from searx.extended_types import sxng_request
from searx.result_types import Answer
from searx.result_types.answer import BaseAnswer

from . import Answerer, AnswererInfo

kw2func = [
    ("min", min),
    ("max", max),
    ("avg", lambda args: sum(args) / len(args)),
    ("sum", sum),
    ("prod", lambda args: reduce(mul, args, 1)),
]

def roll_dice(dice_expressions):
    rolls = []
    for expr in dice_expressions:
        expr = expr.lower()
        if 'd' not in expr:
            continue
        try:
            x_str, y_str = expr.split('d', 1)
            x = int(x_str) if x_str else 1
            y = int(y_str)
            if x <= 0 or y <= 0:
                continue
            for _ in range(x):
                rolls.append(random.randint(1, y))
        except ValueError:
            continue
    return rolls

class SXNGAnswerer(Answerer):
    """Statistics functions"""

    keywords = [kw for kw, _ in kw2func] + ["dice"]

    def info(self):
        return AnswererInfo(
            name=gettext(self.__doc__),
            description=gettext("Compute {func} of the arguments".format(func='/'.join(self.keywords))),
            keywords=self.keywords,
            examples=["avg 123 548 2.04 24.2", "dice 2d6 1d20"],
        )

    def answer(self, query: str) -> list[BaseAnswer]:
        results = []
        parts = query.strip().split()
        if len(parts) < 2:
            return results

        # Handle "dice" keyword
        if parts[0].lower() == "dice":
            rolls = roll_dice(parts[1:])

            if not rolls:
                return results

            result_str = ", ".join(str(r) for r in rolls)
            results.append(Answer(answer=result_str))
            return results

        # Standard statistics handling (min, max, avg, sum, prod)
        ui_locale = babel.Locale.parse(sxng_request.preferences.get_value('locale'), sep='-')

        try:
            args = [babel.numbers.parse_decimal(num, ui_locale, numbering_system="latn") for num in parts[1:]]
        except Exception:
            return results

        for k, func in kw2func:
            if k == parts[0]:
                res = func(args)
                res = babel.numbers.format_decimal(res, locale=ui_locale)
                f_str = ', '.join(babel.numbers.format_decimal(arg, locale=ui_locale) for arg in args)
                results.append(Answer(answer=f"[{ui_locale}] {k}({f_str}) = {res} "))
                break

        return results