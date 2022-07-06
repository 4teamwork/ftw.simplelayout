from ftw.upgrade import UpgradeStep


class AddMediaFolder(UpgradeStep):
    """Add Media Folder.
    """

    def __call__(self):
        self.install_upgrade_profile()
