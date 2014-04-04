from Products.Five.browser import BrowserView
import json


class SimplelayoutInfo(BrowserView):

    def get_simplelayout_config(self):
        view = self.context.restrictedTraverse(self.context.getLayout())

        return json.loads(view.load_default_settings())
