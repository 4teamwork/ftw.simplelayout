from ftw.simplelayout.behaviors import ITeaser
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.interfaces import IBlockConfiguration
from plone.memoize.instance import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


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

    def get_image(self):

        if self.context.image:
            return IMG_TAG_TEMPLATE.format(
                **dict(
                    src=self._get_image_scale_url(),
                    floatClass=self._get_image_scale(),
                    alt=self.context.Title()
                ))
        else:
            return None

    @memoize
    def _get_image_scale(self):
        return IBlockConfiguration(self.context).load().get('scale', '')

    def _get_image_scale_url(self):
        scale = self._get_image_scale()

        if scale:
            scaler = self.context.restrictedTraverse('@@images')
            return scaler.scale('image', scale=scale).url
        else:
            return self.context.absolute_url() + '/@@images/image'
