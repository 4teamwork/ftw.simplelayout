from ftw.upgrade import UpgradeStep


class AddAdditionalOpengraphTags(UpgradeStep):
    """Add additional opengraph tags
    """

    def __call__(self):
        self.install_upgrade_profile()
