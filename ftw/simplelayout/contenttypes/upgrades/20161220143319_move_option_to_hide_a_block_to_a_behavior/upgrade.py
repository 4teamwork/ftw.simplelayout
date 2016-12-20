from ftw.upgrade import UpgradeStep


class MoveOptionToHideABlockToABehavior(UpgradeStep):
    """Move option to hide a block to a behavior.
    """

    def __call__(self):
        self.install_upgrade_profile()
