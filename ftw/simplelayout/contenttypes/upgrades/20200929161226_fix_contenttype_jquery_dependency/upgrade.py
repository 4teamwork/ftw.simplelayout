from ftw.simplelayout.utils import IS_PLONE_5
from ftw.upgrade import UpgradeStep


class FixContenttypeJqueryDependency(UpgradeStep):
    """Fix contenttype jquery dependency.
    """

    def __call__(self):
        if IS_PLONE_5:
            self.install_upgrade_profile()
