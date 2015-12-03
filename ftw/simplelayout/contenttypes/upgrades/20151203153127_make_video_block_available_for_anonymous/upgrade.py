from ftw.upgrade import UpgradeStep


class MakeVideoBlockAvailableForAnonymous(UpgradeStep):
    """Make video block available for anonymous.
    """

    def __call__(self):
        self.install_upgrade_profile()
