from collections import OrderedDict
from ftw.simplelayout import _
from ftw.simplelayout.browser.actions import DefaultActions
from ftw.simplelayout.contenttypes.contents.interfaces import IGalleryBlock
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from zope import schema
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implements


class IGalleryBlockSchema(form.Schema):
    """GalleryBlock for simplelayout
    """

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    show_title = schema.Bool(
        title=_(u'label_show_title', default=u'Show title'),
        default=True,
        required=False)

    is_hidden = schema.Bool(
        title=_(u'label_is_hidden', default=u'Hide the block'),
        description=_(
            u'description_is_hidden',
            default=u'This will visually hide the block. This is not a '
                    u'security feature, the block and its content can '
                    u'still be accessed.'),
        default=False,
        required=False)


alsoProvides(IGalleryBlockSchema, IFormFieldProvider)


class GalleryBlock(Container):
    implements(IGalleryBlock)


class GalleryBlockActions(DefaultActions):

    def specific_actions(self):
        return OrderedDict([
            ('upload', {
                'class': 'upload icon-image-upload',
                'title': translate(
                    _(u'label_upload', default=u'Upload'),
                    context=self.request),
                'href': './sl-ajax-upload-block-view'
            }),
            ('folderContents', {
                'class': 'icon-folder-contents redirect',
                'title': translate(
                    _(u'label_folder_contents_images',
                      default=u'Go to folder contents for managing images'),
                    context=self.request),
                'href': '/folder_contents'
            }),
        ])
