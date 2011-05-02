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
import BTrees
import operator
import pytz
from Acquisition import aq_base, aq_inner, aq_parent
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from datetime import datetime
from persistent import Persistent
from random import randint
from zope import annotation, component, interface

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

    def __len__(self):
        return len(self._archive)

    def archiveContent(self, content):
        return self._archive.archiveContent(content)

    def restoreContent(self, id):
        return self._archive.restoreContent(id)

    def listArchivedContent(self, **filters):
        return self._archive.listArchivedContent(**filters)

    def clearArchive(self, **filters):
        return self._archive.clearArchive(**filters)


def _now():
    return datetime.now(pytz.UTC)


def _datetimeToIndex(dt):
    """Convert a datetime.datetime to an index integer

    We index on a per-day resolution.

    """
    if dt.tzinfo:
        dt = dt.astimezone(pytz.UTC)
    return dt.toordinal() # Don't you love the stdlib?


class ArchivedContent(Persistent):
    interface.implements(IContentArchive)

    _items = None
    _bydate = None
    _byparent = None

    def __init__(self):
        self._setup()

    def _setup(self):
        self._length = BTrees.Length.Length()
        self._items = BTrees.IOBTree.IOBTree()
        self._byparent = BTrees.OOBTree.OOBTree()
        self._bydate = BTrees.IOBTree.IOBTree()

    def _index(self, entry):
        """Insert entry into the archive"""

        # Generate a new id, basically the Zope ZCatalog id generation code
        id_ = getattr(self, '_v_nextid', 0)
        if id_ % 4000 == 0:
            id_ = randint(-2000000000, 2000000000)
        while not self._items.insert(id_, entry):
            id_ = randint(-2000000000, 2000000000)
        self._v_nextid = id_ + 1
        entry['id'] = id_
                
        parentUID = entry['parent']
        byparent = self._byparent.get(parentUID)
        if byparent is None:
            byparent = self._byparent[parentUID] = BTrees.IIBTree.IITreeSet()
        byparent.insert(id_)

        dateentry = _datetimeToIndex(entry['timestamp'])
        bydate = self._bydate.get(dateentry)
        if bydate is None:
            bydate = self._bydate[dateentry] = BTrees.IIBTree.IITreeSet()
        bydate.insert(id_)

        self._length.change(1)

        return id_

    def _unindex(self, entry):
        """Remove entry from the archive"""

        id_ = entry['id']

        parentUID = entry['parent']
        byparent = self._byparent.get(parentUID)
        if byparent is not None:
            byparent.remove(id_)
            if not byparent:
                del self._byparent[parentUID]

        dateentry = _datetimeToIndex(entry['timestamp'])
        bydate = self._bydate.get(dateentry)
        if bydate is not None:
            bydate.remove(id_)
            if not bydate:
                del self._bydate[dateentry]

        del self._items[id_]

        self._length.change(-1)

    def __len__(self):
        return self._length()

    def archiveContent(self, content):
        parent = aq_parent(aq_inner(content))

        site = component.getUtility(ISiteRoot)
        pm = getToolByName(site, 'portal_membership')
        user = pm.getAuthenticatedMember()
        user_id = user.getId()
        uf_path = aq_parent(aq_parent(user)).getPhysicalPath()

        entry = dict(
            originalId=content.getId(),
            title=content.Title(),
            parent=parent.UID(),
            user=(uf_path, user_id),
            timestamp = _now(),
            item=aq_base(content),
        )

        parent.manage_delObjects(content.getId())

        return self._index(entry)

    def restoreContent(self, id_):
        entry = self._items.get(id_)
        if entry is None:
            raise KeyError('No such archived content: %d' % id_)

        self._unindex(entry)

        # Find parent
        site = component.getUtility(ISiteRoot)
        uidcat = getToolByName(site, 'uid_catalog')
        results = uidcat(UID=entry['parent'])
        if not results:
            raise KeyError('No parent %s found for archived item %s' % (
                entry['parent'], id_))
        parent = results[0].getObject()

        # Determine the id under which to store the object
        if getattr(aq_base(parent), 'has_key', None) is not None:
            has_id = lambda x, p=parent: p.has_key(x)
        else:
            # For Plone 3 we still need to list all ids of a folder
            has_id = lambda x, p=parent.objectIds(): x in p
        newid = entry['originalId']
        pattern = '%s-%%d' % newid
        idx = 0
        while has_id(newid):
            idx += 1
            newid = pattern % idx
        if newid != entry['originalId']:
            entry['item']._setId(newid)

        # Restore
        parent._setObject(newid, entry['item'])
        del entry

        return parent._getOb(newid)

    def listArchivedContent(self, **filters):
        ids = None
        if 'parentUID' in filters:
            ids = self._byparent.get(filters['parentUID'])
            if not ids:
                return []
        if 'before' in filters:
            before = _datetimeToIndex(filters['before'])
            values = self._bydate.values(None, before)
            values = BTrees.IIBTree.multiunion(values)
            ids = BTrees.IIBTree.intersection(ids, values)
            if not ids:
                return []
        if ids is None:
            ids = self._items.keys()

        # Gather results and sort
        result = []
        for id_ in ids:
            entry = self._items[id_].copy()
            result.append(entry)
        result.sort(key=operator.itemgetter('timestamp'))
        result.reverse()

        return result

    def clearArchive(self, **filters):
        if filters:
            counter = 0
            for entry in self.listArchivedContent(**filters):
                counter += 1
                self._unindex(self._items[entry['id']])
                del entry
        else:
            counter = len(self)
            self._setup()
        return counter
