from ftw.referencewidget.widget import ReferenceBrowserWidget
from ftw.simplelayout import _
from plone.autoform.interfaces import IFormFieldProvider
from plone.behavior.interfaces import IBehaviorAssignable
from plone.directives.form import widget
from plone.supermodel import model
from z3c.relationfield.event import _setRelation
from z3c.relationfield.interfaces import IRelation
from z3c.relationfield.interfaces import IRelationList
from z3c.relationfield.schema import Relation
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Invalid
from zope.interface import invariant
from zope.interface import provider
from zope.schema import getFields


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


@provider(IFormFieldProvider)
class IHiddenBlock(model.Schema):

    is_hidden = schema.Bool(
        title=_(u'label_is_hidden', default=u'Hide the block'),
        description=_(
            u'description_is_hidden',
            default=u'This will visually hide the block. This is not a '
                    u'security feature, the block and its content can '
                    u'still be accessed.'),
        default=False,
        required=False,
    )


@provider(IFormFieldProvider)
class IMediaFolderReference(model.Schema):
    widget('mediafolder',
           ReferenceBrowserWidget,
           allow_nonsearched_types=True,
           start='parent',
           override=True,
           selectable=['ftw.simplelayout.MediaFolder', ])
    mediafolder = Relation(
        title=_(u'label_mediafolder', default=u'Mediafolder reference'),
        required=False,
    )


def custom_extract_relations(obj):
    assignable = IBehaviorAssignable(obj, None)
    if assignable is None:
        return
    for behavior in assignable.enumerateBehaviors():
        # The original methods checks for this...
        # if behavior.marker == behavior.interface:
        #     continue
        # But the behavior this should not happen in order to habe refs indexed
        # while adding.
        # This worked on edit because of the LinkIntegrity feature, which
        # updates all realtions upon modifications.
        for name, field in getFields(behavior.interface).items():
            if IRelation.providedBy(field):
                try:
                    relation = getattr(behavior.interface(obj), name)
                except AttributeError:
                    continue
                yield behavior.interface, name, relation
            if IRelationList.providedBy(field):
                try:
                    rel_list = getattr(behavior.interface(obj), name)
                except AttributeError:
                    continue
                if rel_list is not None:
                    for relation in rel_list:
                        yield behavior.interface, name, relation


def add_behavior_relations(obj, event):
    """Register relations in behaviors.
    This event handler fixes a bug in plone.app.relationfield, which only
    updates the zc.catalog when an object gets modified, but not when it gets
    added.
    """
    for behavior_interface, name, relation in custom_extract_relations(obj):
        _setRelation(obj, name, relation)
