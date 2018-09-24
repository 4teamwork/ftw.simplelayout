from ftw.simplelayout.images.configuration import Configuration
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from plone import api
import transaction


class TestImageConfigurationImageLimits(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def _set_image_limit(self, value):
        api.portal.set_registry_record(
            name='image_limits',
            value=value,
            interface=ISimplelayoutDefaultSettings)

        transaction.commit()

    def test_format_with_no_configuration(self):
        self._set_image_limit({})
        self.assertEqual({}, Configuration().image_limits())

    def test_format_with_only_one_limit_type(self):
        self._set_image_limit({
            'example.contenttype_1': [u'soft: width=400']
            })

        self.assertDictEqual(
            {'example.contenttype_1': {
                'soft': {
                    'width': 400,
                }
            }},
            Configuration().image_limits())

    def test_format_with_soft_and_hard_limits(self):
        self._set_image_limit({
            'example.contenttype_1': [
                u'soft: width=400, height=200',
                u'hard: width=300',
                ]
            })

        self.assertDictEqual(
            {'example.contenttype_1': {
                'soft': {
                    'width': 400,
                    'height': 200,
                },
                'hard': {
                    'width': 300,
                }
            }},
            Configuration().image_limits())

    def test_format_with_multiple_contenttypes(self):
        self._set_image_limit({
            'example.contenttype_1': [
                u'soft: width=400, height=200',
                u'hard: width=300',
                ],
            'example.contenttype_2': [
                u'soft: width=800',
                ]
            })

        self.assertDictEqual(
            {
                'example.contenttype_1': {
                    'soft': {
                        'width': 400,
                        'height': 200,
                    },
                    'hard': {
                        'width': 300,
                    }
                },
                'example.contenttype_2': {
                    'soft': {
                        'width': 800,
                    }
                }
            },
            Configuration().image_limits())


class TestImageConfigurationIAspectRatios(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def _set_aspect_rations(self, value):
        api.portal.set_registry_record(
            name='image_cropping_aspect_ratios',
            value=value,
            interface=ISimplelayoutDefaultSettings)

        transaction.commit()

    def test_format_with_no_configuration(self):
        self._set_aspect_rations({})
        self.assertEqual({}, Configuration().aspect_ratios())

    def test_format_with_aspect_ratios(self):
        self._set_aspect_rations({
            'example.contenttype_1': [u'4/3 => 1.33333', u'16/9 => 1.7777']
            })

        self.assertDictEqual({
            'example.contenttype_1': [
                {'title': '4/3', 'value': '1.33333'},
                {'title': '16/9', 'value': '1.7777'},
            ]}, Configuration().aspect_ratios())

    def test_format_with_multiple_contenttypes(self):
        self._set_aspect_rations({
            'example.contenttype_1': [u'4/3 => 1.33333', u'16/9 => 1.7777'],
            'example.contenttype_2': [u'Free => 0']
            })

        self.assertDictEqual({
            'example.contenttype_1': [
                {'title': '4/3', 'value': '1.33333'},
                {'title': '16/9', 'value': '1.7777'},
            ],
            'example.contenttype_2': [
                {'title': 'Free', 'value': '0'},
            ]}, Configuration().aspect_ratios())
