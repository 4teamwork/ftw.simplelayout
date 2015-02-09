from Products.Five.browser import BrowserView


class BaseBlock(BrowserView):

    def __call__(self):
        return self.template()
