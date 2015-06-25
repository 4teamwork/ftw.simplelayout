from plone.app.imaging.utils import getAllowedSizes
from Products.Five.browser import BrowserView


class GalleryBlockView(BrowserView):
    """GalleryBlock default view"""

    def get_images(self):
        return self.context.listFolderContents(
            contentFilter=self._build_query)

    def get_box_boundaries(self):
        return getAllowedSizes().get('simplelayout_galleryblock')

    @property
    def _build_query(self):
        query = {}
        query['portal_type'] = ['Image']
        return query
