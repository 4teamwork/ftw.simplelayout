from ftw.simplelayout.images.interfaces import IImageLimitValidatorMessages
from Products.Five.browser import BrowserView


class LowImageQualityIndicator(BrowserView):

    def low_quality_limit_str(self):
        return IImageLimitValidatorMessages(self.context).limit_str('soft')
