from Products.Five.browser import BrowserView
from Acquisition import aq_inner


class RedirectToParent(BrowserView):

    def __call__(self):
        context = aq_inner(self.context).aq_explicit
        #auto redirect to the anchor
        param = '/#%s' % context.id

        return self.context.REQUEST.RESPONSE.redirect(
            context.aq_parent.absolute_url()+param)
