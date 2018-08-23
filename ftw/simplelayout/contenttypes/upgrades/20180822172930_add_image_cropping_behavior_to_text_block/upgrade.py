from ftw.upgrade import UpgradeStep


class AddImageCroppingBehaviorToTextBlock(UpgradeStep):
    """Add image cropping behavior to text block.
    """

    def __call__(self):
        self.install_upgrade_profile()
