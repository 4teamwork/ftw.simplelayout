from Acquisition._Acquisition import aq_inner
from ftw.simplelayout.browser.blocks.base import BaseBlock
from ftw.simplelayout.contenttypes.behaviors import ITeaser
from ftw.simplelayout.contenttypes.contents.textblock import ITextBlockSchema
from ftw.simplelayout.interfaces import ISimplelayoutActions
from ftw.simplelayout.utils import normalize_portal_type
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter


class TextBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/textblock.pt')

    @property
    def teaser_url(self):
        teaser = ITeaser(self.context)
        if not teaser:
            return None

        if teaser.internal_link and teaser.internal_link.to_object:
            return teaser.internal_link.to_object.absolute_url()
        elif teaser.external_link:
            return teaser.external_link
        else:
            return None

    def get_image_data(self):
        """
        This method returns a dictionary containing all the data needed
        to render the image in the template.
        """
        if not self.context.image:
            return

        data = {
            'wrapper_css_classes': ' '.join(
                ['sl-image', self._get_image_scale_name(),
                 self._get_image_float()]
            ),
            'link_url': '',
            'link_title': self.context.Title(),
            'link_css_classes': '',
            'image_tag': self._get_image_scale().tag(
                alt=ITextBlockSchema(self.context).image_alt_text or '',
                title=None,
                height=None,
                width=None
            ),
        }

        if self.teaser_url:
            data.update({
                'link_url': self.teaser_url,
            })
            return data

        if self.context.open_image_in_overlay:
            # Get the scale defined in `ftw.colorbox`.
            image_scale = self._get_image_scale('colorbox')
            # Don't fail if the scale has been removed in the policy.
            link_url = image_scale.url if image_scale else ''

            data.update({
                'link_url': link_url,
                'link_css_classes': 'colorboxLink',
            })
            return data

        return data

    @memoize
    def _get_image_scale_name(self):
        scale = self.blockconfig.get('scale', '')
        if scale:
            return scale
        else:
            return self._get_default_scale()

    def _get_image_scale(self, scale=None):
        if not scale:
            scale = self._get_image_scale_name()
        scaler = self.context.restrictedTraverse('@@images')
        return scaler.scale('image', scale=scale)

    @memoize
    def _get_default_actions(self):
        normalized_portal_type = normalize_portal_type(
            self.context.portal_type)

        actions = queryMultiAdapter(
            (self.context, self.request),
            ISimplelayoutActions,
            name='{0}-actions'.format(normalized_portal_type))
        return actions.specific_actions().items()[0][1]

    @memoize
    def _get_default_scale(self):
        return self._get_default_actions()['data-scale']

    @memoize
    def _get_image_float(self):
        image_float = self.blockconfig.get('imagefloat', '')

        if image_float:
            return image_float
        else:
            return self._get_default_image_float()

    @memoize
    def _get_default_image_float(self):
        return self._get_default_actions()['data-imagefloat']

    @property
    def can_add(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, 'portal_membership')
        permission = mtool.checkPermission(
            'ftw.simplelayout: Add TextBlock', context)
        return bool(permission)
