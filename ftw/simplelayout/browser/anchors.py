from Products.TinyMCE.browser.interfaces.anchors import IAnchorView
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from lxml.html import fromstring
from plone.app.textfield import IRichText
from plone.dexterity.utils import iterSchemata
from Products.Five.browser import BrowserView
from zope.interface import implements
from zope.schema import getFieldsInOrder


SEARCHPATTERN = "a"


class BlockAnchorsView(BrowserView):
    implements(IAnchorView)

    def listAnchorNames(self, *args, **kwargs):
        anchors = []
        query = {'object_provides': ISimplelayoutBlock.__identifier__}

        for block in self.context.listFolderContents(contentFilter=query):
            fields = self.get_html_fields(block)

            for field in fields:
                anchors.extend(
                    self.extract_anchors(
                        field.get(block).output
                    )
                )

        return anchors

    def get_html_fields(self, obj):
        fields = []
        for schema in iterSchemata(obj):
            for name, field in getFieldsInOrder(schema):
                # Only consider RichText fields.
                if IRichText.providedBy(field):
                    fields.append(field)

        # Filter empty fields (i.e. not having a value).
        fields = filter(lambda field: field.get(obj), fields)

        # Only consider fields containing HTML.
        fields = filter(lambda field: 'html' in field.output_mime_type, fields)

        return fields

    def extract_anchors(self, text):
        if not text:
            return []
        tree = fromstring(text)
        return [
            anchor.get('name') for anchor in tree.findall(SEARCHPATTERN)
            if "name" in anchor.keys()
        ]
