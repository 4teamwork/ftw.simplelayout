from ftw.upgrade import UpgradeStep


class RegisterShowroomGalleryJavascript(UpgradeStep):
    """Register showroom gallery javascript.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.setup_install_profile('profile-ftw.showroom:default')
