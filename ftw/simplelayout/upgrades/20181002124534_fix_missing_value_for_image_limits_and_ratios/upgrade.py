from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.upgrade import UpgradeStep
from plone import api


class FixMissingValueForImageLimitsAndRatios(UpgradeStep):
    """Fix missing value for image limits and ratios.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.set_default_value_for('image_limits', {})
        self.set_default_value_for('image_cropping_aspect_ratios', {})

    def set_default_value_for(self, name, value):
        if api.portal.get_registry_record(
                name=name, interface=ISimplelayoutDefaultSettings):
            return

        api.portal.set_registry_record(
            name=name,
            value=value,
            interface=ISimplelayoutDefaultSettings)
