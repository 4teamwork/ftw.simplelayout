from ftw.upgrade import UpgradeStep


class AddNewGalleryBlockImageScaling(UpgradeStep):
    """Add new gallery block image scaling.
    """

    def __call__(self):
        self.install_upgrade_profile()
