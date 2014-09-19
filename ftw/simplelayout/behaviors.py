from ftw.simplelayout import _
from plone.behavior import AnnotationStorage
from plone.directives import form
from plone.formwidget.contenttree import ObjPathSourceBinder
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import Invalid
from zope.interface import invariant
from plone.behavior.interfaces import ISchemaAwareFactory


class ITeaser(form.Schema):
    """Add internal and external link field."""

    form.fieldset(
        'teaser',
        label=_(u'Teaser'),
        fields=('external_link', 'internal_link')
    )

    external_link = schema.URI(
        title=_(u'label_external_link', default=u'External URL'),
        required=False)

    internal_link = RelationChoice(
        title=_(u'label_internal_link', default=u'Internal link'),
        source=ObjPathSourceBinder(),
        required=False,
    )

    @invariant
    def link_invariant(data):
        if data.external_link and data.internal_link:
            raise Invalid(_(
                u"It's not possible to have an internal_link and an "
                u"external_link together"))

alsoProvides(ITeaser, form.IFormFieldProvider)
