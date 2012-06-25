from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from unittest2 import TestCase
import transaction


class TestSampleTypes(TestCase):

    layer = FTW_SIMPLELAYOUT_INTEGRATION_TESTING

    def setUp(self):
        super(TestSampleTypes, self).setUp()

        portal = self.layer['portal']
        self.portal_url = self.layer['portal'].portal_url()

        self.demo_folder = portal.get(portal.invokeFactory(
            'Folder', 'demo-folder'))
        transaction.commit()

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_NAME, TEST_USER_PASSWORD, ))

    def test_add_types(self):
        self.browser.open(
            self.portal_url + '/demo-folder/createObject?type_name=Page')
        self.browser.getControl(name='title').value= u"A test page"
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test page', self.browser.contents)

        self.browser.open(
            self.portal_url + '/demo-folder/a-test-page/createObject?type_name=Paragraph')
        self.browser.getControl(name='title').value= u"A test paragraph"
        self.browser.getControl(name='form.button.save').click()
        self.browser.open(
            self.portal_url + '/demo-folder/a-test-page/a-test-paragraph')
        self.assertIn('A test paragraph', self.browser.contents)


    def tearDown(self):
        super(TestSampleTypes, self).tearDown()

        portal = self.layer['portal']
        portal.manage_delObjects(['demo-folder'])
        transaction.commit()
