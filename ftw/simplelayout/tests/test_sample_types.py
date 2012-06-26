from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing.z2 import Browser
from unittest2 import TestCase
import transaction
import StringIO


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
        # Page
        self.browser.open(
            self.portal_url + '/demo-folder/createObject?type_name=Page')
        self.browser.getControl(name='title').value= u"A test page"
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test page', self.browser.contents)

        # Paragraph
        self.browser.open(
            self.portal_url + '/demo-folder/a-test-page/createObject?type_name=Paragraph')
        self.browser.getControl(name='title').value= u"A test paragraph"
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test paragraph', self.browser.contents)

        # Link
        self.browser.open(
            self.portal_url + '/demo-folder/a-test-page/createObject?type_name=LinkBlock')
        self.browser.getControl(name='title').value= u"A test link"
        self.browser.getControl(name='remoteUrl').value= u"http://www.4teamwork.ch"
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test link', self.browser.contents)
        self.assertIn('http://www.4teamwork.ch', self.browser.contents)

        # File
        self.browser.open(
            self.portal_url + '/demo-folder/a-test-page/createObject?type_name=FileBlock')
        self.browser.getControl(name='title').value= u"A test file"
        ctrl = self.browser.getControl(name='file_file')
        ctrl.add_file(StringIO.StringIO('File contents'),
                     'text/plain', 'test.txt')
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test file', self.browser.contents)

        # Image
        self.browser.open(
            self.portal_url + '/demo-folder/a-test-page/createObject?type_name=ImageBlock')
        self.browser.getControl(name='title').value= u"A test image"
        ctrl = self.browser.getControl(name='image_file')
        ctrl.add_file(StringIO.StringIO('Image contents'),
                     'image/gif', 'test.gif')
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test image', self.browser.contents)



    def tearDown(self):
        super(TestSampleTypes, self).tearDown()

        portal = self.layer['portal']
        portal.manage_delObjects(['demo-folder'])
        transaction.commit()
