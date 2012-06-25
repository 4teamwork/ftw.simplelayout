from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from ftw.simplelayout import config
from Products.ATContentTypes.content import document
from ftw.simplelayout.contents.interfaces import IParagraph

from ftw.simplelayout import _

schema = atapi.Schema((
    atapi.BooleanField(
        'showTitle',
        schemata='default',
        default=0,
        widget=atapi.BooleanWidget(
            label=_(u"label_show_title", default="Show Title"),
         )),
    atapi.TextField(
        'text',
        required=False,
        searchable=True,
        default_input_type='text/html',
        default_output_type='text/html',
        widget=atapi.RichWidget(
            label=_(u'label_body_text', default=u'Body Text'),
            rows=25,
            filter_buttons=('image', ))),
    ))

paragraph_schema = document.ATDocumentSchema.copy() + schema.copy()
paragraph_schema['excludeFromNav'].default = True
paragraph_schema['title'].required = False
paragraph_schema['description'].widget.visible = -1


class Paragraph(document.ATDocument):
    security = ClassSecurityInfo()
    implements(IParagraph)
    schema = paragraph_schema


atapi.registerType(Paragraph, config.PROJECTNAME)
