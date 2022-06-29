from Products.Five.browser import BrowserView
from plone import api


class MediaFolderView(BrowserView):

    def __call__(self):
        base_url = self.context.absolute_url()
        can_list_contents = api.user.has_permission('List folder contents', obj=self.context)
        if api.user.is_anonymous() or not can_list_contents:
            return self.request.RESPONSE.redirect(base_url + '/@@view')
        else:
            return self.request.RESPONSE.redirect(base_url + '/folder_contents')
