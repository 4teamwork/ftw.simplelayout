from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from plone import api
from zope.interface import implementer
import json


@implementer(IImageLimits)
class ImageLimits(object):
    limit_configuration = {}

    def __init__(self, context):
        self.context = context
        self._load_limit_configuration()

    def validate(self, limit_type, identifier,
                 width=None, height=None):
        """Validates if the given limit_type (hard/soft) is satisfied for the
        given identifier.

        This method returns true if:

        - there is no configuration for this identifier
        - there is no configuration for the limit_type
        - there is no configuration for the requested dimension
        - the configured limits are respected
        """
        limits = self.get_limits_for(limit_type, identifier)
        if self._validate(width, limits.get('width', 0)) and \
                self._validate(height, limits.get('height', 0)):
            return True
        return False

    def get_limits_for(self, limit_type, identifier):
        """Returns the defined limits for the given identifier:

        i.e. {'width': 100, 'height': 150}
        """
        limit_config = self.limit_configuration.get(identifier, {})

        return limit_config.get(limit_type, {})

    def has_low_quality_image(self, image, identifier):
        """Returns true or false, depending if the soft limit of the image
        of the given context is satisfied or not.
        """
        if not image:
            return False
        return not self.validate('soft', identifier, image._width, image._height)

    def _validate(self, current, expected):
        if not current or not expected:
            return True
        return current >= expected

    def _load_limit_configuration(self):
        self.limit_configuration = json.loads(self._limit_configuration_json)

    @property
    def _limit_configuration_json(self):
        return api.portal.get_registry_record(
            name='image_limits', interface=ISimplelayoutDefaultSettings)
