# Archiving tool, stores archived content for later retrieval
# 
# Things to note on the archived content:
#  - Original parent UID
#  - Original id
#  - Time of archiving
#  - User that archived the item?
#  - basic DublinCore data (non-dynamic)
#
# Indexes on tool:
#  - Path
#  - Time of archiving
# 
# Information available from archive:
#  - count
#  - per-path info, sorted on time or title or id
#  - per-item: id, original path
#
# To really archive content, we:
#   - Delete the content from the original place to ensure the site (through
#     events and such) believes the content to be gone.
#   - Store the content locally in a wrapping structure with metadata so 
#     there is no acquisition context or something for ZopeFind to find.
# 
# Strategy:
#   - Make this a utility, with storage in an annotation on the portal root.
#   - A control panel can provide views into this, including debugging tools.
#   - Not making this a classic ZMI-based tool let's us avoid all the classic
#     Zope2 sit-ups and the possibility for acquisition context and traversal
#     to trigger all the wrong plone site hooks.
from zope import interface

from plone.app.archive.interfaces import IContentArchive

class ContentArchive(object):
    interface.implements(IContentArchive)
