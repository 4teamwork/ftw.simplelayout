from ftw.upgrade import UpgradeStep


class ConfigureAddableTypes(UpgradeStep):
    """Configure addable types.
    """

    def __call__(self):
        self.install_upgrade_profile()
