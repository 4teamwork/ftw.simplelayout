from ftw.upgrade import UpgradeStep


class RemoveClientSideStyling(UpgradeStep):
    """Remove client side styling.
    """

    def __call__(self):
        self.install_upgrade_profile()
