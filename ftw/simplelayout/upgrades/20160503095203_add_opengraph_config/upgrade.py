from ftw.upgrade import UpgradeStep


class AddOpengraphConfig(UpgradeStep):
    """Add opengraph config.
    """

    def __call__(self):
        self.install_upgrade_profile()
