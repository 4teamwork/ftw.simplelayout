from ftw.referencewidget.widget import ReferenceBrowserWidget
from ftw.simplelayout import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.directives.form import widget
from plone.supermodel import model
from z3c.relationfield.schema import Relation
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.interface import invariant


class ITeaser(model.Schema):
    """Add internal and external link field."""

    model.fieldset(
        'teaser',
        label=_(u'Teaser'),
        fields=('external_link', 'internal_link'),
        description=_(
            u"description_teaser_fieldset",
            default=(
                u"Use the teaser to redirect to another content or website."
                u"The title and the image of the block will be used to show a link")
        )
    )

    external_link = schema.URI(
        title=_(u'label_external_link', default=u'External URL'),
        required=False)

    widget('internal_link',
           ReferenceBrowserWidget,
           allow_nonsearched_types=True)
    internal_link = Relation(
        title=_(u'label_internal_link', default=u'Internal link'),
        required=False,
    )

    @invariant
    def link_invariant(data):
        if data.external_link and data.internal_link:
            raise Invalid(_(
                u"It's not possible to have an internal_link and an "
                u"external_link together"))

alsoProvides(ITeaser, IFormFieldProvider)
