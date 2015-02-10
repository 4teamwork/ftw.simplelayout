from ftw.simplelayout.behaviors import ITeaser
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.simplelayout.browser.blocks.base import BaseBlock


IMG_TAG_TEMPLATE = (
    '<div class="sl-image {floatClass}">'
    '<img src="{src}" alt="{alt}" />'
    '</div>')


class TextBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/textblock.pt')

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

    @property
    def _cssClass(self):
        return 'sl-full'

    def get_image(self):
        if self.context.image:
            return IMG_TAG_TEMPLATE.format(
                **dict(
                    src=self.context.absolute_url() + '/@@images/image',
                    floatClass=self._cssClass,
                    alt=self.context.Title()
                ))
        else:
            return None
