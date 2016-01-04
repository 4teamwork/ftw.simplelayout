from ftw.upgrade import UpgradeStep


class RegisterXHRHTTPErrorHandlerJavascript(UpgradeStep):
    """Register xhrhttp error handler javascript.
    """

    def __call__(self):
        self.install_upgrade_profile()
