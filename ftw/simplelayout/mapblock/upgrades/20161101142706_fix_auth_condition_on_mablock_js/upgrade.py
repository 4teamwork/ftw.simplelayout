from ftw.upgrade import UpgradeStep


class FixAuthConditionOnMablockJS(UpgradeStep):
    """Fix auth condition on mablock JS.
    """

    def __call__(self):
        self.install_upgrade_profile()
