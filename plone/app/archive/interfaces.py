from zope import interface

class IContentArchive(interface.Interface):
    def __len__():
        """Return how many items have been archived."""

    def archiveContent(content):
        """Archive a given content item.

        Returns the id of the archived content.

        """

    def restoreContent(id):
        """Restore a piece of archived content in it's original location.

        id is the internal content-archive id as returned by
        listArchivedContent.

        Returns the restored content.

        """

    def listArchivedContent(**filters):
        """List archived content

        Returns a sequence of items sorted by date descending.
        Items are dictionaries with id, Title, parentUID, date and user
        keys, where the latter reflect the user and datetime.datetime of
        archiving.

        Currently supported filters:

          * parentUID: UID of parent where the content originally lived
          * before:    datetime.datetime to limit listing to.

        """

    def clearArchive(**filters):
        """Permanently remove archived content

        Permanently delete archived content. Filters are the same as for
        listing archived content.

        Returns how many archived items were cleared.

        """
