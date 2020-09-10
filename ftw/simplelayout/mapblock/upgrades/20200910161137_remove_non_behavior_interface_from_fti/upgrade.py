from ftw.upgrade import UpgradeStep


class RemoveNonBehaviorInterfaceFromFTI(UpgradeStep):
    """Remove non behavior interface from FTI.
    """

    def __call__(self):
        self.install_upgrade_profile()
