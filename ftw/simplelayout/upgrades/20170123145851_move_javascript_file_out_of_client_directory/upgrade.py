from ftw.upgrade import UpgradeStep


class MoveJavascriptFileOutOfClientDirectory(UpgradeStep):
    """Move javascript file out of client directory.
    """

    def __call__(self):
        self.install_upgrade_profile()
