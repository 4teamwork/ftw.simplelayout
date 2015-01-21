from ftw.simplelayout.behaviors import ITeaser
from plone.uuid.interfaces import IUUID
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.publisher.browser import BrowserView


class TextBlockView(BrowserView):

    template = ViewPageTemplateFile('templates/textblock.pt')

    def __call__(self):

        return self.template()

    def additional(self):
        teaser_url = self.teaser_url()
        if teaser_url:
            return 'data-simplelayout-url="{0}"'.format(teaser_url)
        else:
            return ''

    def teaser_url(self):
        teaser = ITeaser(self.context)
        if not teaser:
            return None

        if teaser.internal_link:
            return teaser.internal_link.to_object.absolute_url()
        elif teaser.external_link:
            return teaser.external_link
        else:
            return None
