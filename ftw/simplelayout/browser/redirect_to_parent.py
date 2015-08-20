from Acquisition import aq_inner
from plone import api
from Products.Five.browser import BrowserView


def redirect_to_parent(context):
    context = aq_inner(context).aq_explicit
    # Auto redirect to the anchor
    param = '#{0}'.format(context.id)
    return context.REQUEST.RESPONSE.redirect(
        context.aq_parent.absolute_url() + param)


class RedirectToParent(BrowserView):

    def __call__(self):
        return redirect_to_parent(self.context)


class BlockContainerRedirectToParent(RedirectToParent):

    def __call__(self):
        if api.user.is_anonymous():
            return super(BlockContainerRedirectToParent, self).__call__()
        else:
            context = aq_inner(self.context).aq_explicit
            return self.request.RESPONSE.redirect(
                context.absolute_url() + '/folder_contents')
