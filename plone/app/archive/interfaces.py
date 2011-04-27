from zope import interface

class IContentArchive(interface.Interface):
    def archiveContent(self, content):
        """Archive a given content item"""

    def restoreContent(self, id):
        """Restore a piece of archived content in it's original location.

        id is the internal content-archive id as returned by
        listArchivedContent.

        """

    def listArchivedContent(self, **filters):
        """List archived content

        Returns a sequence of items sorted by date descending.
        Items are dictionaries with id, Title, parentUID, date and user
        keys, where the latter reflect the user and datetime.datetime of
        archiving.

        Currently supported filters:

          * parentUID: UID of parent where the content originally lived
          * before:    datetime.datetime to limit listing to.

        """

    def clearArchive(self, **filters):
        """Permanently remove archived content

        Permanently delete archived content. Filters are the same as for
        listing archived content.

        """
