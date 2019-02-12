from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_PAM_TESTING
from unittest2 import TestCase


class TestPloneAppMultilingualStagingSupport(TestCase):
    layer = FTW_SIMPLELAYOUT_CONTENT_PAM_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test(self):
        baseline = create(Builder('sl content page').titled(u'A page'))
        create(Builder('sl textblock').within(baseline))
        self.assertFalse(IStaging(baseline).is_baseline())
        working_copy = IStaging(baseline).create_working_copy(self.portal)
        self.assertTrue(IStaging(baseline).is_baseline())
        self.assertFalse(IStaging(working_copy).is_baseline())
