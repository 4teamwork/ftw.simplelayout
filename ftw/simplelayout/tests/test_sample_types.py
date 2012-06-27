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
        self.page = self.demo_folder.get(self.demo_folder.invokeFactory(
            'Page', 'demo-page'))
        transaction.commit()

        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.browser.addHeader('Authorization', 'Basic %s:%s' % (
            TEST_USER_NAME, TEST_USER_PASSWORD, ))

    def test_add_page(self):
        # Page
        self.browser.open(
            self.portal_url + '/demo-folder/createObject?type_name=Page')
        self.browser.getControl(name='title').value= u"A test page"
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test page', self.browser.contents)

    def test_add_paragraph_and_view(self):
        self.browser.open(
            self.page.absolute_url() + '/createObject?type_name=Paragraph')
        self.browser.getControl(name='title').value= u"A test paragraph"
        self.browser.getControl(name='text').value= u"Some text"
        self.browser.getControl(name='showTitle:boolean').value = True
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test paragraph', self.browser.contents)
        self.assertIn('Some text', self.browser.contents)

    def test_paragraph_show_title(self):
        self.browser.open(
            self.page.absolute_url() + '/createObject?type_name=Paragraph')
        self.browser.getControl(name='title').value= u"Not visible"
        self.browser.getControl(name='text').value= u"Some other text"
        self.browser.getControl(name='showTitle:boolean').value = False
        self.browser.getControl(name='form.button.save').click()
        self.assertNotIn('Not visible', self.browser.contents)
        self.assertIn('Some other text', self.browser.contents)

    def test_add_link_and_view(self):
        self.browser.open(
            self.page.absolute_url() + '/createObject?type_name=LinkBlock')
        self.browser.getControl(name='title').value= u"A test link"
        self.browser.getControl(
            name='remoteUrl').value= u"http://www.4teamwork.ch"
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test link', self.browser.contents)
        self.assertIn('http://www.4teamwork.ch', self.browser.contents)

    def test_add_file_and_view(self):
        self.browser.open(
            self.page.absolute_url() + '/createObject?type_name=FileBlock')
        self.browser.getControl(name='title').value= u"A test file"
        ctrl = self.browser.getControl(name='file_file')
        ctrl.add_file(StringIO.StringIO('File contents'),
                     'text/plain', 'test.txt')
        self.browser.getControl(name='form.button.save').click()
        self.assertIn('A test file', self.browser.contents)

    def test_add_image_and_view(self):
        self.browser.open(
            self.page.absolute_url() + '/createObject?type_name=ImageBlock')
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
