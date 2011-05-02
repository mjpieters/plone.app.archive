from Products.PloneTestCase import ptc
from datetime import datetime
from zope import component

from plone.app.archive.tests.layer import integrationlayer


class IntegrationTests(ptc.PloneTestCase):
    layer = integrationlayer

    testnow = None

    def afterSetUp(self):
        from plone.app.archive import archive
        self._normal_now = archive._now
        def _testingnow():
            return self.testnow or self._normal_now()
        archive._now = _testingnow

    def beforeTearDown(self):
        from plone.app.archive import archive
        archive._now = self._normal_now

    def _getArchive(self):
        from plone.app.archive.interfaces import IContentArchive
        return component.getUtility(IContentArchive)

    def test_listEmptyArchive(self):
        archive = self._getArchive()
        self.assertEqual(archive.listArchivedContent(), [])

    def test_clearEmptyArchive(self):
        archive = self._getArchive()
        self.assertEqual(archive.clearArchive(), 0)

    def test_sizeOfEmptyArchive(self):
        archive = self._getArchive()
        self.assertEqual(len(archive), 0)

    def test_restoreNonExistingContent(self):
        archive = self._getArchive()
        self.assertRaises(KeyError, archive.restoreContent, 12345)

    def test_archiveContent(self):
        archive = self._getArchive()
        archive.archiveContent(self.folder.document1)
        self.assertFalse('document1' in self.folder.contentIds())
        self.assertEqual(len(self.portal.portal_catalog(getId='document1')), 0)

    def test_restoreContent(self):
        archive = self._getArchive()
        archiveid = archive.archiveContent(self.folder.document1)
        archive.restoreContent(archiveid)
        self.assertTrue('document1' in self.folder.contentIds())
        self.assertEqual(len(self.portal.portal_catalog(getId='document1')), 1)

    def test_restoreContentWithIdConflict(self):
        archive = self._getArchive()
        archiveid = archive.archiveContent(self.folder.document1)
        self.folder.invokeFactory('Document', 'document1', title='New doc')
        archive.restoreContent(archiveid)
        self.assertEqual(sorted(self.folder.contentIds()),
            ['document1', 'document1-1', 'subfolder'])

    def test_restoreContentParentGone(self):
        archive = self._getArchive()
        archiveid = archive.archiveContent(self.folder.subfolder.document2)
        self.folder.manage_delObjects('subfolder')
        self.assertRaises(KeyError, archive.restoreContent, archiveid)

    def test_listArchivedContent(self):
        archive = self._getArchive()
        self.testnow = datetime(1995, 8, 20, 21, 5, 3)
        doc = self.folder.document1.aq_base
        archiveid = archive.archiveContent(self.folder.document1)
        archived = archive.listArchivedContent()
        self.assertEqual(len(archive), len(archived))

        expected = dict(
            id=archiveid,
            originalId='document1',
            title='Document 1',
            parent=self.folder.UID(),
            user=(('', 'plone', 'acl_users'), ptc.default_user),
            timestamp=self.testnow,
            item=doc,
        )
        self.assertEqual(archived[0], expected)

    def test_listArchivedContentByParent(self):
        archive = self._getArchive()
        archiveid1 = archive.archiveContent(self.folder.document1)
        archiveid2 = archive.archiveContent(self.folder.subfolder.document2)

        res = archive.listArchivedContent(parentUID=self.folder.UID())
        self.assertEqual([e['id'] for e in res], [archiveid1])
        res = archive.listArchivedContent(parentUID=self.folder.subfolder.UID())
        self.assertEqual([e['id'] for e in res], [archiveid2])

    def test_listArchivedContentByDate(self):
        archive = self._getArchive()
        self.testnow = datetime(2000, 1, 1, 10, 20, 00)
        archiveid1 = archive.archiveContent(self.folder.document1)
        self.testnow = datetime(2005, 1, 1, 10, 20, 00)
        archiveid2 = archive.archiveContent(self.folder.subfolder.document2)

        res = archive.listArchivedContent(before=datetime.now())
        self.assertEqual([e['id'] for e in res], [archiveid2, archiveid1])
        res = archive.listArchivedContent(before=datetime(2003, 1, 1))
        self.assertEqual([e['id'] for e in res], [archiveid1])
        res = archive.listArchivedContent(before=datetime(1999, 12, 31))
        self.assertEqual(res, [])

    def test_listArchivedContentByParentAndByDate(self):
        archive = self._getArchive()
        self.testnow = datetime(2000, 1, 1, 10, 20, 00)
        archive.archiveContent(self.folder.document1)
        self.testnow = datetime(2005, 1, 1, 10, 20, 00)
        archiveid2 = archive.archiveContent(self.folder.subfolder.document2)

        res = archive.listArchivedContent(
            before=datetime.now(), parentUID=self.folder.subfolder.UID())
        self.assertEqual([e['id'] for e in res], [archiveid2])
        res = archive.listArchivedContent(
            before=datetime(2003, 1, 1), parentUID=self.folder.subfolder.UID())
        self.assertEqual(res, [])

    def test_clearArchiveByParent(self):
        archive = self._getArchive()
        archiveid1 = archive.archiveContent(self.folder.document1)
        archive.archiveContent(self.folder.subfolder.document2)
        archive.clearArchive(parentUID=self.folder.subfolder.UID())
        self.assertEqual(len(archive), 1)

        res = archive.listArchivedContent()
        self.assertEqual([e['id'] for e in res], [archiveid1])
        res = archive.listArchivedContent(parentUID=self.folder.subfolder.UID())
        self.assertEqual([e['id'] for e in res], [])


def test_suite():
    import unittest
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
