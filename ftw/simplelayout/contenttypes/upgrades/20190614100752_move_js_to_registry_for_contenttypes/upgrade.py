from ftw.simplelayout.utils import IS_PLONE_5
from ftw.upgrade import UpgradeStep
from plone import api


class MoveJSToRegistryForMapblockForPlone5(UpgradeStep):
    """Move JS to registry for mapblock. Only for plone 5
    """

    def __call__(self):

        if IS_PLONE_5:
            self.install_upgrade_profile()

            record = 'plone.bundles/plone-legacy.resources'
            resources = api.portal.get_registry_record(record)
            name = u'resource-ftw-simplelayout-videoblock-js'
            if name in resources:
                resources.remove(name)
