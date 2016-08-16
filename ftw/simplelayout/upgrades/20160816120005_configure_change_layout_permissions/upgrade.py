from ftw.upgrade import UpgradeStep


class ConfigureChangeLayoutPermissions(UpgradeStep):
    """Configure change layout permissions.
    """

    def __call__(self):
        self.install_upgrade_profile()
