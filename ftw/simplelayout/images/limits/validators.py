from ftw.simplelayout import _
from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.simplelayout.images.interfaces import IImageLimitValidatorMessages
from ftw.simplelayout.images.limits.limits import Limits
from z3c.form import validator
from zope.interface import implementer
from zope.interface import Invalid


class LimitValidatorMessages(object):
    def __init__(self):
        self.limits = Limits()

    def limit_not_satisfied_message(self, limit_type, identifier, image):
        if limit_type == 'soft':
            return self._soft_limit_not_satisfied_message(identifier, image)
        elif limit_type == 'hard':
            return self._hard_limit_not_satisfied_message(identifier, image)

        return ''

    def limit_str(self, limit_type, identifier, image):
        limits = self._get_image_limits_for(limit_type, identifier)

        current_width = image._width
        current_height = image._height

        width = limits.get('width', 0)
        height = limits.get('height', 0)

        width_str = self._width_str(width, current_width)
        height_str = self._height_str(height, current_height)

        limit_str = ''
        if width and height:
            limit_str = _(u'limit_width_and_height',
                          default=u"${width_str} and ${height_str}",
                          mapping={'width_str': width_str, 'height_str': height_str})
        elif width:
            limit_str = width_str

        elif height:
            limit_str = height_str

        return limit_str

    def _hard_limit_not_satisfied_message(self, identifier, image):
        limit_str = self.limit_str('hard', identifier, image)

        return _(u'hard_limit_not_satisfied',
                 default=u"The image doesn't fit the required dimensions of ${limit_str}",
                 mapping={'limit_str': limit_str})

    def _soft_limit_not_satisfied_message(self, identifier, image):
        limit_str = self.limit_str('soft', identifier, image)

        return _(u'soft_limit_not_satisfied',
                 default=u"Optimal image quality: ${limit_str}",
                 mapping={'limit_str': limit_str})

    def _width_str(self, width, current_width):
        return _(u'limit_width_str',
                 default=u"width: ${width}px (current: ${current_width}px)",
                 mapping={'width': width, 'current_width': current_width}
                 )

    def _height_str(self, height, current_height):
        return _(u'limit_height_str',
                 default=u"height: ${height}px (current: ${current_height}px)",
                 mapping={'height': height, 'current_height': current_height}
                 )

    def _get_image_limits_for(self, limit_type, identifier):
        return self.limits.get_limits_for(limit_type, identifier)


@implementer(IImageLimitValidatorMessages)
class ImageLimitValidatorMessages(object):
    def __init__(self, context):
        self.context = context
        self.limit_validator_messages = LimitValidatorMessages()
        self.image_limits = IImageLimits(self.context)

    def limit_not_satisfied_message(self, limit_type):
        return self.limit_validator_messages.limit_not_satisfied_message(
            limit_type, self.image_limits.identifier, self.image_limits._image)

    def limit_str(self, limit_type):
        return self.limit_validator_messages.limit_str(
            limit_type, self.image_limits.identifier, self.image_limits._image)


class ImageLimitValidator(validator.SimpleFieldValidator):
    """Validates the image-dimensions.

    Soft-limit: Validates if the given image has at least the dimensions given
    within the ImageLimit-configuration for the current contenttype.

    Hard-limit: Validates if the given image has at least the dimensions given
    within the ImageLimit-configuration for the current contenttype.
    """

    # The identifier should be the name of your contenttype. Because we
    # don't know the contenttype within a SimpleFieldValidator on an add-form,
    # we have to define it here explicitly.
    identifier = None

    def __init__(self, *args, **kwargs):
        super(ImageLimitValidator, self).__init__(*args, **kwargs)
        self.limits = Limits()
        self.validator_messages = LimitValidatorMessages()

    def validate(self, value):
        super(ImageLimitValidator, self).validate(value)
        if not value:
            return

        self._validate_hard_limit(value)

    def _validate_hard_limit(self, value):
        if not self._validate_limit_for('hard', value):
            raise Invalid(self.validator_messages.limit_not_satisfied_message(
                'hard', self.identifier, value))

    def _validate_limit_for(self, limit_type, value):
        return self.limits.validate(
            limit_type, self.identifier, width=value._width, height=value._height)
