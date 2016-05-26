from ftw.upgrade import UpgradeStep


class RegisterRequestTrackerJavascript(UpgradeStep):
    """Register RequestTracker javascript.
    """

    def __call__(self):
        self.install_upgrade_profile()
