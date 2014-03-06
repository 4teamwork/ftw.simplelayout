from ftw.simplelayout.interfaces import IDisplaySettings
from zope.component import queryMultiAdapter
from zope.publisher.browser import BrowserView
import cssutils


def parse_css(styles, attr):
    parsed = cssutils.parseStyle(styles)
    value = getattr(parsed, attr)
    if not value:
        return None

    value = value.rstrip('px')
    return value


class TextBlockView(BrowserView):

    def get_scaled_image(self):
        scale = self.context.restrictedTraverse('@@images')
        displaysettings = queryMultiAdapter((self.context, self.request),
                                            IDisplaySettings)
        styles = displaysettings.get_image_styles()

        # ridiculous large height, so it doesn't matters while scaling
        height = 10000

        if not styles:
            # XXX: Get defaults from registry or current contentpage
            contentwidth = 960
            images = 2
            columns = 4
            width = contentwidth / columns / images

            return scale.scale('image', width=width, height=height)
        else:
            width = int(parse_css(styles, 'width'))
            return scale.scale('image', width=width, height=height)

    def img_tag(self):
        """Manually create image tag, because we set width and height width
        the style attribute to not break the columns in simplelayout.
        """
        displaysettings = queryMultiAdapter((self.context, self.request),
                                            IDisplaySettings)
        styles = displaysettings.get_image_styles()
        scale = self.get_scaled_image()
        return ('<img src="{url}" alt="{title}" title="{title}"'
                'width="{width}" height="{height}"'
                'style="{style}" />'.format(**{'url': scale.url,
                                               'title': self.context.Title(),
                                               'width': scale.width,
                                               'height': scale.height,
                                               'style': styles}))
