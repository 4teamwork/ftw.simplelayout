from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.simplelayout.utils import IS_PLONE_5
from ftw.testbrowser import browser as defaultbrowser
from ftw.testbrowser import browsing
from plone.dexterity.interfaces import IDexterityFTI
from plone.protect import createToken
from zope.component import getUtility


class TestDropZoneUpload(SimplelayoutTestCase):
    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    @browsing
    def test_create_files_in_filelistingblock(self, browser):
        listing = create(Builder('sl listingblock').titled(u'Downloads')
                         .within(create(Builder('sl content page')
                                 .titled(u'Page'))))
        self.assertEquals([], listing.objectIds())

        browser.login()
        self.make_dropzone_upload(listing, self.asset('world.txt').open('rb'))
        self.assertEqual(201, browser.status_code)
        self.assertEqual({u'content': u'Created',
                          u'url': u'http://nohost/plone/page/downloads/world.txt',
                          u'proceed': True}, browser.json)
        self.assertEquals(['world.txt'], listing.objectIds())

        doc, = listing.objectValues()
        self.assertEquals('File', doc.portal_type)
        self.assertEquals('world.txt', doc.Title())
        if IS_PLONE_5:
            self.assertEquals('Hello World', doc.file.data.strip())
        else:
            self.assertEquals('Hello World', doc.getFile().data.strip())

    @browsing
    def test_create_ftw_files_in_filelistingblock(self, browser):
        """
        Ensure filelistingblock uploads can be configured to create
        ftw.file.File
        """
        fti = getUtility(IDexterityFTI,
                         name='ftw.simplelayout.FileListingBlock')
        act = list(fti.allowed_content_types)
        act.insert(0, 'ftw.file.File')
        fti.allowed_content_types = tuple(act)

        listing = create(Builder('sl listingblock').titled(u'Downloads')
                         .within(create(Builder('sl content page')
                                 .titled(u'Page'))))
        self.assertEquals([], listing.objectIds())

        browser.login()
        self.make_dropzone_upload(listing, self.asset('world.txt').open('rb'))
        self.assertEqual(201, browser.status_code)
        self.assertEqual(
            {u'content': u'Created',
             u'url': u'http://nohost/plone/page/downloads/world.txt',
             u'proceed': True},
            browser.json
        )
        self.assertEquals(['world.txt'], listing.objectIds())

        doc, = listing.objectValues()
        self.assertEquals('ftw.file.File', doc.portal_type)

    @browsing
    def test_create_images_in_galleries(self, browser):
        gallery = create(Builder('sl galleryblock').titled(u'Gallery')
                         .within(create(Builder('sl content page').titled(u'Page'))))
        self.assertEquals([], gallery.objectIds())

        browser.login()
        self.make_dropzone_upload(gallery, self.asset('cropped.jpg').open('rb'))
        self.assertEqual(201, browser.status_code)
        self.assertEqual({u'content': u'Created',
                          u'url': u'http://nohost/plone/page/gallery/cropped.jpg',
                          u'proceed': True}, browser.json)
        self.assertEquals(['cropped.jpg'], gallery.objectIds())

        img, = gallery.objectValues()
        self.assertEquals('Image', img.portal_type)
        self.assertEquals('cropped.jpg', img.Title())

    @browsing
    def test_files_are_not_allowed_in_galleries(self, browser):
        gallery = create(Builder('sl galleryblock').titled(u'Gallery')
                         .within(create(Builder('sl content page').titled(u'Page'))))
        self.assertEquals([], gallery.objectIds())

        with browser.login().expect_http_error(400):
            self.make_dropzone_upload(gallery, self.asset('world.txt').open('rb'))

        self.assertEqual({u'error': u'Only images can be added to the gallery.',
                          u'proceed': False}, browser.json)
        self.assertEquals([], gallery.objectIds())

    def make_dropzone_upload(self, context, file_):
        """The dropzone JS makes a multipart upload with the the file as field named "file".
        The testbrowser does not support making multipart requests directly (we would have to
        create the MIME body ourself), but the form filling does that well.
        Therefore we use an HTML form for uploading.
        """
        html = (
            '<form action="{}/@@dropzone-upload" method="post" enctype="multipart/form-data">'
            '  <input type="file" name="file" />'
            '  <input type="hidden" name="_authenticator" value="{}" />'
            '  <input type="submit" />'
            '</form>').format(context.absolute_url(), createToken())

        defaultbrowser.open(context).parse(html)
        defaultbrowser.fill({'file': file_}).submit()
        return defaultbrowser
