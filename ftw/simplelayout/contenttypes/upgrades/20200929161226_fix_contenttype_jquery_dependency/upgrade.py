from ftw.upgrade import UpgradeStep


class FixContenttypeJqueryDependency(UpgradeStep):
    """Fix contenttype jquery dependency.
    """

    def __call__(self):
        self.install_upgrade_profile()
