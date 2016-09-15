from ftw.upgrade import UpgradeStep


class ProtectShowHideTitleField(UpgradeStep):
    """Protect show/hide title field.
    """

    def __call__(self):
        self.install_upgrade_profile()
