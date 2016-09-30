from ftw.upgrade import UpgradeStep


class RemovePrecookedCSSFiles(UpgradeStep):
    """Remove precooked CSS files.
    """

    def __call__(self):
        self.install_upgrade_profile()
