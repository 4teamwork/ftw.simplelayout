from ftw.upgrade import UpgradeStep


class AddImageLimits(UpgradeStep):
    """Add image limits.
    """

    def __call__(self):
        self.install_upgrade_profile()
