from ftw.simplelayout import _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.interface import provider


class IImageCroppingMarker(Interface):
    """
    """


@provider(IFormFieldProvider)
class IImageCropping(model.Schema):

    model.fieldset('image_cropping',
                   label=_(u'Image cropping'),
                   fields=['use_cropped_image_for_overlay',
                           'cropped_image',
                           'cropped_config'])

    use_cropped_image_for_overlay = schema.Bool(
        title=_(u'use_cropped_image_for_overlay',
                default=u'Use cropped image for overlay'),
        required=False,
        default=True,
        missing_value=True)

    form.mode(cropped_image='hidden')
    cropped_image = NamedBlobImage(
        title=_(u'label_cropped_image', default=u'Cropped Image'),
        required=False)

    form.mode(cropped_image='hidden')
    cropped_config = schema.TextLine(
        title=_(u'label_cropped_config', default=u'The final cropped area position and size data'),
        required=False)

