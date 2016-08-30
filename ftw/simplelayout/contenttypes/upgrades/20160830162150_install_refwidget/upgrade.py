from ftw.upgrade import UpgradeStep


class InstallRefwidget(UpgradeStep):
    """Install the reference widget from "ftw.referencewidget"
    """

    def __call__(self):
        self.setup_install_profile('profile-ftw.referencewidget:default')
