from plone.app.imaging.utils import getAllowedSizes
from Products.Five.browser import BrowserView


class GalleryBlockView(BrowserView):
    """GalleryBlock default view"""

    def get_images(self):
        return self.context.listFolderContents(
            contentFilter=dict(portal_type=['Image']))

    def get_box_boundaries(self):
        return getAllowedSizes().get('simplelayout_galleryblock')
