from Products.PloneTestCase import ptc
from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class IntegrationTestLayer(tcl_ptc.BasePTCLayer):
    """Integration tests layer with some default content"""

    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.folder.invokeFactory('Document', 'document1', title='Document 1')

        self.folder.invokeFactory('Folder', 'subfolder')
        subfolder = self.folder.subfolder
        subfolder.invokeFactory('Document', 'document2', title='Document 2')

integrationlayer = IntegrationTestLayer([tcl_ptc.ptc_layer])
