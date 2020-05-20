from Products.CMFCore.utils import getToolByName


def uninstall(self):
    setup_tool = getToolByName(self, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(
        'profile-ftw.simplelayout.aliasblock:uninstall',
        ignore_dependencies=True)
