from ftw.simplelayout.utils import IS_PLONE_5
from ftw.upgrade import UpgradeStep
from plone import api


class MoveMapblockJsFromLegacyToItsOwnBundle(UpgradeStep):
    """Move mapblock js from legacy to its own bundle.
    """

    def __call__(self):

        if IS_PLONE_5:
            self.install_upgrade_profile()

            record = 'plone.bundles/plone-legacy.resources'
            resources = api.portal.get_registry_record(record)
            name = u'resource-ftw-simplelayout-mapblock-resources'
            if name in resources:
                resources.remove(name)
