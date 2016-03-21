from ftw.upgrade import UpgradeStep


class FixSimplelayoutImageScalingDimensions(UpgradeStep):
    """Fix simplelayout image scaling dimensions.
    """

    def __call__(self):
        self.install_upgrade_profile()
