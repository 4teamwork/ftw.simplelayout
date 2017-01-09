from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from plone.app.textfield.value import RichTextValue
from unittest2 import TestCase


class TestPageAnchors(TestCase):
    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def test_anchors(self):
        """
        This test makes sure that `ContentPageAnchorView` is able
        to extract the anchors form the text blocks of a content page.
        """

        contentpage = create(Builder('sl content page').titled(u'The Page'))
        create(Builder('sl textblock')
               .within(contentpage)
               .having(text=RichTextValue(
                   u'<p>Lorem <a name="anchor-textblock1"></a> '
                   u'ipsum dolor sit amet.</p>')))
        create(Builder('sl textblock')
               .within(contentpage)
               .having(text=RichTextValue(
                   u'<p>Lorem <a name="anchor-textblock2"></a> '
                   u'ipsum dolor sit amet.</p>')))

        view = contentpage.restrictedTraverse('content_anchors')
        anchor_names = view.listAnchorNames()
        self.assertEqual(['anchor-textblock1', 'anchor-textblock2'],
                         anchor_names)
