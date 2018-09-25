from ftw.simplelayout import _
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope import schema
from zope.interface import provider


@provider(IFormFieldProvider)
class ICroppedImageInOverlay(model.Schema):
    model.fieldset('image',
                   fields=['use_cropped_image_for_overlay'])

    use_cropped_image_for_overlay = schema.Bool(
        title=_(u'use_cropped_image_for_overlay',
                default=u'Use cropped image for overlay'),
        description=_(u'use_cropped_image_for_overlay_desc',
                      default=u'If you crop an image, the original image will be still available. '
                              u'Per default, the original image will be used for the overlay. '
                              u'If you want to show the cropped image instead, mark this option.'),
        required=False,
        default=True,
        missing_value=True)


@provider(IFormFieldProvider)
class IImageCropping(model.Schema):

    # This field should be hidden. Unfortunately, that's not possible due to a
    # weird bug in the file-selector-widget.
    # If this field is hidden and contains an image, it will raise a validation
    # error on form-save. If we skip the validation of this field, the image will
    # be broken after saving. So, we just hide this field through css.
    #
    # WARNING: This case is not testet. I can't reproduce this issue in the test.
    #
    # form.mode(cropped_config='hidden')
    cropped_image = NamedBlobImage(
        title=_(u'label_cropped_image', default=u'Cropped Image'),
        required=False)

    form.mode(cropped_config='hidden')
    cropped_config = schema.TextLine(
        title=_(u'label_cropped_config', default=u'The final cropped configuration'),
        required=False)
