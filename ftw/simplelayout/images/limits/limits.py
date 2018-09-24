from ftw.simplelayout.images.configuration import Configuration
from ftw.simplelayout.images.cropping.behaviors import IImageCropping
from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.simplelayout.images.interfaces import IImageLimitValidatorMessages
from zope.interface import implementer


class Limits(object):
    limit_configuration = {}

    def __init__(self):
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

    def _validate(self, current, expected):
        if not current or not expected:
            return True
        return current >= expected

    def _load_limit_configuration(self):
        self.limit_configuration = Configuration().image_limits()


@implementer(IImageLimits)
class ImageLimits(object):
    limitsCls = Limits
    image_field_name = 'image'

    def __init__(self, context):
        self.context = context
        self.limits = self.limitsCls()
        self.identifier = self.context.portal_type

    def validate(self, limit_type):
        return self.limits.validate(
            limit_type, self.identifier,
            self._image._width, self._image._height)

    def get_limits_for(self, limit_type):
        return self.limits.get_limits_for(limit_type, self.identifier)

    def get_all_limits(self):
        return self.limits.get_all_limits_for(self.identifier)

    def has_low_quality_image(self):
        """Returns true or false, depending if the soft limit of the image
        of the given context is satisfied or not.
        """
        if not self._image:
            return False
        return not self.validate('soft')

    def low_quality_image_message(self):
        return IImageLimitValidatorMessages(self.context).limit_str(
            'soft', self.identifier, self._image)

    @property
    def _image(self):
        image = getattr(self.context, self.image_field_name)
        if IImageCropping.providedBy(self.context):
            image = self.context.cropped_image or image
        return image
