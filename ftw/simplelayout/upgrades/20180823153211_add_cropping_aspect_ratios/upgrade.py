from ftw.upgrade import UpgradeStep


class AddCroppingAspectRatios(UpgradeStep):
    """Add cropping aspect ratios.
    """

    def __call__(self):
        self.install_upgrade_profile()
