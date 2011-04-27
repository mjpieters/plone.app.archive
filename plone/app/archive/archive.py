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
from persistent import Persistent
from zope import annotation, component, interface
from Products.CMFCore.interfaces import ISiteRoot

from plone.app.archive.interfaces import IContentArchive


ARCHIVE_KEY = 'plone.app.archive'
class ContentArchive(object):
    """Wrapper for ArchivedContent

    Looks up the local (per-site) ArchivedContent instance and delegates all
    API calls to it.

    """
    interface.implements(IContentArchive)

    @property
    def _archive(self):
        site = component.getUtility(ISiteRoot)
        ann = annotation.interfaces.IAnnotations(site)
        if ARCHIVE_KEY not in ann:
            ann[ARCHIVE_KEY] = ArchivedContent()
        return ann[ARCHIVE_KEY]

    def archiveContent(self, content):
        return self._archive.archiveContent(content)

    def restoreContent(self, id):
        return self._archive.restoreContent(id)

    def listArchivedContent(self, **filters):
        return self._archive.listArchivedContent(**filters)

    def clearArchive(self, **filters):
        return self._archive.clearArchive(**filters)


class ArchivedContent(Persistent):
    interface.implements(IContentArchive)

    def archiveContent(self, content):
        pass

    def restoreContent(self, id):
        pass

    def listArchivedContent(self, **filters):
        pass

    def clearArchive(self, **filters):
        pass
