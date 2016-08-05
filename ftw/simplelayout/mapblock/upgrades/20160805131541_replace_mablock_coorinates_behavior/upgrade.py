from ftw.upgrade import UpgradeStep


class ReplaceMablockCoorinatesBehavior(UpgradeStep):
    """Replace mablock coorinates behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
