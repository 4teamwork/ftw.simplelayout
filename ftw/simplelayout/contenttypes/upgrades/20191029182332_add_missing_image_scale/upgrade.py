from ftw.upgrade import UpgradeStep


class AddMissingImageScale(UpgradeStep):
    """Add missing image scale.
    """

    def __call__(self):
        self.install_upgrade_profile()
