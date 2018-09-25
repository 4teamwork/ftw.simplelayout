from ftw.simplelayout import _
from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.simplelayout.images.interfaces import IImageLimitValidatorMessages
from Products.Five.browser import BrowserView


class LimitIndicator(BrowserView):

    limit_type = None

    def __init__(self, context, request):
        super(LimitIndicator, self).__init__(context, request)
        self.image_limits = IImageLimits(self.context)
        self.limit_validator_messages = IImageLimitValidatorMessages(self.context)

    def __call__(self):
        if not self.image_limits.validate('hard'):
            self.limit_type = 'hard'
        elif not self.image_limits.validate('soft'):
            self.limit_type = 'soft'

        return super(LimitIndicator, self).__call__()

    def title(self):
        if self.limit_type == 'hard':
            return _('imageresolution_too_small_label',
                     default="imageresolution is too small")
        elif self.limit_type == 'soft':
            return _('low_quality_image_label', default="low image quality")

    def description(self):
        return self.limit_validator_messages.limit_not_satisfied_message(
            self.limit_type)

    def show_indicator(self):
        return self.limit_type is not None

    def css_klass(self):
        classes = ['limitIndicator']

        if self.limit_type is not None:
            classes.append('{}LimitIndicator'.format(self.limit_type))

        return ' '.join(classes)
