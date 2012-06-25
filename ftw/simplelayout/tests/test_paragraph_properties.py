from ftw.simplelayout.contents.paragraph import Paragraph
from ftw.simplelayout.tests import test_singleview_block_properties
from ftw.testing import MockTestCase


TestSingleViewBlockProperties = \
    test_singleview_block_properties.TestSingleViewBlockProperties


class TestParagraphProperties(TestSingleViewBlockProperties):

    def setUp(self):
        MockTestCase.setUp(self)

        self.context = Paragraph('test-paragraph')
        self.request = self.stub_request()
