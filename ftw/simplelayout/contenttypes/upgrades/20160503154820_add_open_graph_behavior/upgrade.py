from ftw.upgrade import UpgradeStep


class AddOpenGraphBehavior(UpgradeStep):
    """Add open graph behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
