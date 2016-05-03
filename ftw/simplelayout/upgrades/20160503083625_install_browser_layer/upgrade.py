from ftw.upgrade import UpgradeStep


class InstallBrowserLayer(UpgradeStep):
    """Install browser layer.
    """

    def __call__(self):
        self.install_upgrade_profile()
