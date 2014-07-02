from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.MimetypesRegistry.MimeTypeItem import guess_icon_path
from plone.memoize.view import memoize
from zope.component import getMultiAdapter


class FileView(BrowserView):

    @memoize
    def getMimeTypeIcon(self):
        context = aq_inner(self.context)
        pstate = getMultiAdapter(
            (context, self.request),
            name=u'plone_portal_state'
        )
        portal_url = pstate.portal_url()
        mtr = getToolByName(context, "mimetypes_registry")
        mime = list(mtr.lookup(context.file.contentType))
        mime.append(mtr.lookupExtension(context.file.filename))
        mime.append(mtr.lookup("application/octet-stream")[0])

        icon_paths = [m.icon_path for m in mime if m.icon_path]
        if icon_paths:
            return icon_paths[0]

        return portal_url + "/" + guess_icon_path(mime[0])
