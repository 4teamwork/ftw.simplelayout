from ftw.upgrade import UpgradeStep


class FixDefaultPageForm(UpgradeStep):
    """Fix default page form.
    """

    def __call__(self):
        self.install_upgrade_profile()
