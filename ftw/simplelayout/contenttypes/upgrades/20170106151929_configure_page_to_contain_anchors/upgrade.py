from ftw.upgrade import UpgradeStep


class ConfigurePageToContainAnchors(UpgradeStep):
    """Configure page to contain anchors.
    """

    def __call__(self):
        self.install_upgrade_profile()
