from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from plone import api
from zope.interface import implementer
import json



class Limits(object):

    @classmethod
    def validate(kls, limit_type, identifier=None,
                 width=None, height=None):
        """Validates if the given limit_type (hard/soft) is satisfied for the
        given identifier.

        This method returns true if:

        - there is no configuration for this identifier
        - there is no configuration for the limit_type
        - there is no configuration for the requested dimension
        - the configured limits are respected
        """
        limits = kls.get_limits_for(limit_type, identifier)
        if self._validate(width, limits.get('width')) and \
                kls._validate(height, limits.get('height')):
            return True
        return False

    @classmethod
    def get_limits_for(kls, limit_type, identifier):
        """Returns the defined limits for the given identifier:

        i.e. {'width': 100, 'height': 150}
        """
        limit_config = self.limit_configuration.get(identifier, {})
        limits = {
            'width': 0,
            'height': 0
        }
        limits.update(limit_config.get(limit_type, {}))
        return limits

    @classmethod
    def get_all_limits_for(kls, identifier):
        """Returns all defined limit-types for the given identifier:

        i.e. {
            'hard': {'width': 100, 'height': 150},
            'soft': {'width': 200, 'height': 2000}
        }
        """
        return {
            'hard': kls.get_limits_for('hard', identifier),
            'soft': kls.get_limits_for('soft', identifier)
        }

    @classmethod
    def _validate(kls, current, expected):
        if not current or not expected:
            return True
        return current >= expected

    # @classmethod
    # def _load_limit_configuration(kls):
    #     kls.limit_configuration = json.loads(
    #         kls._limit_configuration_json or '{}')

    # @property
    # def _limit_configuration_json(kls):
    #     return api.portal.get_registry_record(
    #         name='image_limits', interface=ISimplelayoutDefaultSettings)


@adapter(Interface)
class ImageLimits(object):
    limits = Limits

    def __init__(self, context):
        self.context = context
        self.request = context.REQUEST

    @property
    def _image(self):
        image = self.image
        if IImageCropping.providedBy(self):
            image = self.cropped_image or self.image

        return image

    def is_low_quality_image(self):
        return self.limits.has_low_quality_image(self._image, self.portal_type)

    def low_quality_image_message(self):
        return self.limits.limit_str(
            'soft', self.portal_type, self._image)



@implementer(IImageLimits)
class ImageLimits(object):
    limit_configuration = {}

    def __init__(self, context):
        self.context = context
        self._load_limit_configuration()

    def validate(self, limit_type, identifier=None,
                 width=None, height=None):
        """Validates if the given limit_type (hard/soft) is satisfied for the
        given identifier.

        This method returns true if:

        - there is no configuration for this identifier
        - there is no configuration for the limit_type
        - there is no configuration for the requested dimension
        - the configured limits are respected
        """
        identifier = identifier or self.context.portal_type
        limits = self.get_limits_for(limit_type, identifier)
        if self._validate(width, limits.get('width')) and \
                self._validate(height, limits.get('height')):
            return True
        return False

    def get_limits_for(self, limit_type, identifier):
        """Returns the defined limits for the given identifier:

        i.e. {'width': 100, 'height': 150}
        """
        limit_config = self.limit_configuration.get(identifier, {})
        limits = {
            'width': 0,
            'height': 0
        }
        limits.update(limit_config.get(limit_type, {}))
        return limits

    def get_all_limits_for(self, identifier):
        """Returns all defined limit-types for the given identifier:

        i.e. {
            'hard': {'width': 100, 'height': 150},
            'soft': {'width': 200, 'height': 2000}
        }
        """
        return {
            'hard': self.get_limits_for('hard', identifier),
            'soft': self.get_limits_for('soft', identifier)
        }

    def has_low_quality_image(self, image=None, identifier=None):
        """Returns true or false, depending if the soft limit of the image
        of the given context is satisfied or not.
        """
        identifier = self.context.portal_type
        if not self._image:
            return False
        return not self.validate('soft', identifier, image._width, image._height)

    @property
    def _image(self):
        image = getattr(self.context, self.image_field_name)
        if IImageCropping.providedBy(self.conext):
            image = self.cropped_image or self.image

        return image

    def _validate(self, current, expected):
        if not current or not expected:
            return True
        return current >= expected

    def _load_limit_configuration(self):
        self.limit_configuration = json.loads(
            self._limit_configuration_json or '{}')

    @property
    def _limit_configuration_json(self):
        return api.portal.get_registry_record(
            name='image_limits', interface=ISimplelayoutDefaultSettings)
