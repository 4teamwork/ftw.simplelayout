from Acquisition import aq_inner
from Products.Five.browser import BrowserView


class RedirectToParent(BrowserView):

    def __call__(self):
        context = aq_inner(self.context).aq_explicit
        # Auto redirect to the anchor
        param = '#{0}'.format(context.id)

        return self.context.REQUEST.RESPONSE.redirect(
            context.aq_parent.absolute_url() + param)
