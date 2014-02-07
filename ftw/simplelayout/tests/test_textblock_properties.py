from ftw.simplelayout.contents.textblock import TextBlock
from ftw.simplelayout.tests import test_singleview_block_properties
from ftw.testing import MockTestCase


TestSingleViewBlockProperties = \
    test_singleview_block_properties.TestSingleViewBlockProperties


class TestParagraphProperties(TestSingleViewBlockProperties):

    def setUp(self):
        MockTestCase.setUp(self)

        self.context = TextBlock('test-paragraph')
        self.request = self.stub_request()
