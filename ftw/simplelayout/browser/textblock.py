from zope.publisher.browser import BrowserView


class TextBlockView(BrowserView):

    def img_tag(self):
        scale = self.context.restrictedTraverse('@@images')
        return scale.scale('image', scale='preview').tag()
