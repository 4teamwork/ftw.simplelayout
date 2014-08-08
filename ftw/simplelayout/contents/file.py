from ftw.simplelayout import _
from ftw.simplelayout.contents.interfaces import IFile
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from plone.namedfile.field import NamedBlobFile
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements


class IFileSchema(form.Schema):
    """TextBlock for simplelayout
    """

    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=False)

    description = schema.Text(
        title=_(u'label_description', default=u'Description'),
        required=False)

    form.primary('file')
    file = NamedBlobFile(
        title=_(u'label_file', default=u'File'),
        required=False)

alsoProvides(IFileSchema, IFormFieldProvider)


class File(Item):
    implements(IFile)
