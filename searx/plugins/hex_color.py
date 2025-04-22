# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring, missing-class-docstring
from __future__ import annotations
import typing

import re

from flask_babel import gettext

from searx.plugins import Plugin, PluginInfo
from searx.result_types import EngineResults

if typing.TYPE_CHECKING:
    from searx.search import SearchWithPlugins
    from searx.extended_types import SXNG_Request


class SXNGPlugin(Plugin):
    """Plugin takes a hex color code starting with #. The results are
    displayed in area for the "answers".
    """

    id = "colorHex_plugin"
    default_on = True
    keywords = ["#"]

    def __init__(self):
        super().__init__()

        self.parser_re = re.compile(f"({'|'.join(self.keywords)}) (.*)", re.I)
        self.info = PluginInfo(
            id=self.id,
            name=gettext("Color Code plugin"),
            description=gettext(
                "Genetes sample color swatches of a given hex color code"),
            examples=["# ffffff"],
            preference_section="query",
        )

#    def post_search(self, request: "SXNG_Request", search: "SearchWithPlugins") -> EngineResults:
#        """Returns a result list only for the first page."""
#        results = EngineResults()
#
#        if search.search_query.pageno > 1:
#            return results
#
#        m = self.parser_re.match(search.search_query.query)
#        if not m:
#            # wrong query
#            return results
#
#        function, string = m.groups()
#        if not string.strip():
#            # end if the string is empty
#            return results
#
#        # make digest from the given string
#        answer = f"https://encycolorpedia.com/{string}.svg"
#
#        results.add(results.types.Answer(answer=answer))
#
#        return results


display_type = ["infobox"]
"""A list of display types composed from ``infobox`` and ``list``.  The latter
one will add a hit to the result list.  The first one will show a hit in the
info box.  Both values can be set, or one of the two can be set."""


def get_results(self, attribute_result, attributes, language):
    search = "SearchWithPlugins"
    results = []

    if search.search_query.pageno > 1:
        return results

    m = self.parser_re.match(search.search_query.query)
    if not m:
        # wrong query
        return results

    function, string = m.groups()
    if not string.strip():
        # end if the string is empty
        return results

    # pylint: disable=too-many-branches
    infobox_title = attribute_result.get('itemLabel')
    infobox_id = attribute_result['item']
    infobox_id_lang = None
    infobox_urls = [None]
    infobox_attributes = [None]
    infobox_content = attribute_result.get('itemDescription', [])
    img_src = f"https://encycolorpedia.com/{string}.svg"
    img_src_priority = 999

    # add the wikidata URL at the end
    infobox_urls.append(
        {'title': 'hex-color', 'url': attribute_result['item']})

    if (
        "list" in display_type
        and img_src is None
        and len(infobox_attributes) == 0
        and len(infobox_urls) == 1
        and len(infobox_content) == 0
    ):
        results.append(
            {'url': infobox_urls[0]['url'], 'title': infobox_title, 'content': infobox_content})
    elif "infobox" in display_type:
        results.append(
            {
                'infobox': infobox_title,
                'id': infobox_id,
                'content': infobox_content,
                'img_src': img_src,
                'urls': infobox_urls,
                'attributes': infobox_attributes,
            }
        )
    return results
