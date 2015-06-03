from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.contents.videoblock import is_vimeo_url
from ftw.simplelayout.contents.videoblock import is_youtube_url
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from plone.uuid.interfaces import IUUID
from unittest2 import TestCase
import json


class TestVideoValidators(TestCase):

    def test_valid_youtube_url(self):
        url = 'https://youtu.be/W42x6-Wf3Cs'
        self.assertTrue(is_youtube_url(url))

        url = 'http://youtu.be/W42x6-Wf3Cs'
        self.assertTrue(is_youtube_url(url))

    def test_invalid_youtube_url(self):
        url = 'https://example.com/W42x6-Wf3Cs'
        self.assertFalse(is_youtube_url(url))

        url = 'https://example.com/W42x6-Wf3Cs/something'
        self.assertFalse(is_youtube_url(url))

        url = 'https://youtu.be/W42x6-Wf3Cs/something'
        self.assertFalse(is_youtube_url(url))

        url = 'https://youtu.be'
        self.assertFalse(is_youtube_url(url))

        url = 'https://youtu.be/'
        self.assertFalse(is_youtube_url(url))

    def test_valid_vimeo_url(self):
        url = 'https://vimeo.com/channels/staffpicks/128510631'
        self.assertTrue(is_vimeo_url(url))

        url = 'http://vimeo.com/channels/staffpicks/128510631'
        self.assertTrue(is_vimeo_url(url))

    def test_invalid_vimeo_url(self):
        url = 'https://vimeo.com/channels/staffpicks/128510631something'
        self.assertFalse(is_vimeo_url(url))

        url = 'https://example.com/channels/staffpicks/128510631'
        self.assertFalse(is_vimeo_url(url))

        url = 'http://vimeo.com/channels/staffpicks/128510631/someting'
        self.assertFalse(is_vimeo_url(url))

        url = 'http://vimeo.com'
        self.assertFalse(is_vimeo_url(url))

        url = 'http://vimeo.com/channels/'
        self.assertFalse(is_vimeo_url(url))


class TestTextBlockRendering(TestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        self.page = create(Builder('sl content page').titled(u'A page'))

    @browsing
    def test_adding_youtube_videoblock(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('VideoBlock')
        browser.fill({'Youtube, or Vimeo URL': 'https://youtu.be/W42x6-Wf3Cs'})
        browser.find_button_by_label('Save').click()
        self.assertTrue(browser.css('.sl-youtube-video'))

    @browsing
    def test_adding_vimeo_videoblock(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('VideoBlock')
        browser.fill({'Youtube, or Vimeo URL': 'https://vimeo.com/channels/staffpicks/128510631'})
        browser.find_button_by_label('Save').click()
        self.assertTrue(browser.css('iframe'))

    @browsing
    def test_youtube_video_view_has_id_based_on_uuid(self, browser):
        videoblock = create(Builder('sl videoblock')
                            .having(video_url='https://youtu.be/W42x6-Wf3Cs')
                            .within(self.page))

        browser.login().visit(videoblock, view='@@block_view')
        self.assertTrue(browser.css('#uuid_{0}'.format(IUUID(videoblock))))

    @browsing
    def test_youtube_video_view_has_videoid(self, browser):
        videoblock = create(Builder('sl videoblock')
                            .having(video_url='https://youtu.be/W42x6-Wf3Cs')
                            .within(self.page))

        browser.login().visit(videoblock, view='@@block_view')
        youtube_config = json.loads(browser.css(
            '.sl-youtube-video').first.attrib['data-youtube'])

        self.assertEquals('W42x6-Wf3Cs', youtube_config['videoId'])

    @browsing
    def test_vimeo_view_iframe_src_contains_videoid(self, browser):
        videoblock = create(Builder('sl videoblock')
                            .having(video_url='https://vimeo.com/channels/staffpicks/128510631')
                            .within(self.page))

        browser.login().visit(videoblock, view='@@block_view')
        iframe_src = browser.css('iframe').first.attrib['src'].split('/')
        self.assertEquals('128510631', iframe_src[-1])

    @browsing
    def test_video_url_invariant(self, browser):
        browser.login().visit(self.page)
        factoriesmenu.add('VideoBlock')
        browser.fill({'Youtube, or Vimeo URL': 'https://example.com'})
        browser.find_button_by_label('Save').click()

        statusmessages.assert_message('There were some errors.')
        self.assertEquals('This is no a valid youtube, or vimeo url.',
                          browser.css('.field.error').first.text)
