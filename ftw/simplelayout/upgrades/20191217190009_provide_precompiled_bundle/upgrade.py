from ftw.simplelayout.utils import IS_PLONE_5
from ftw.upgrade import UpgradeStep


class ProvidePrecompiledBundle(UpgradeStep):
    """Provide precompiled bundle.
    """

    def __call__(self):
        if IS_PLONE_5:
            self.install_upgrade_profile()
