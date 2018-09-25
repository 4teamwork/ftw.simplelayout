from ftw.builder import Builder
from ftw.builder import create
from ftw.simplelayout.images.interfaces import IImageLimits
from ftw.simplelayout.images.limits.limits import Limits
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_CONTENT_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from plone import api
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from zope.interface import Interface
import transaction
import json


FOO_IMAGE_LIMIT_IDENTIFIER = 'foo'
BAR_IMAGE_LIMIT_IDENTIFIER = 'bar'


class IFooSchema(model.Schema):
    """
    """

    image = NamedBlobImage(
        title=u'image',
        required=False)


class IBarSchema(Interface):
    """
    """

    image = NamedBlobImage(
        title=u'image',
        required=False)


class TestLimits(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def limits(self, config):
        limits = Limits()
        limits.limit_configuration = config

        return limits

    def test_do_not_fail_if_no_configuration_is_set(self):
        api.portal.set_registry_record(
            name='image_limits',
            value={},
            interface=ISimplelayoutDefaultSettings)

        transaction.commit()
        limits = self.limits({})

        self.assertEqual({}, limits.limit_configuration)

    def test_validate_limit_returns_true_if_no_field_is_configured(self):
        limits = self.limits({})
        self.assertTrue(
            limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER, width=10))

    def test_validate_limit_returns_true_if_no_limit_type_is_configured(self):
        limits = self.limits({
            FOO_IMAGE_LIMIT_IDENTIFIER: {}
        })

        self.assertTrue(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER, width=10))

    def test_validate_limit_returns_true_if_no_width_and_height_is_configured(self):
        limits = self.limits({
            FOO_IMAGE_LIMIT_IDENTIFIER: {
                'soft': {}
            }
        })

        self.assertTrue(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER, width=10))

    def test_validate_limit_returns_true_if_no_width_and_height_is_given(self):
        limits = self.limits({
            FOO_IMAGE_LIMIT_IDENTIFIER: {
                'soft': {
                    'width': 100,
                    'height': 100
                }
            }
        })

        self.assertTrue(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER))

    def test_validate_limits(self):
        limits = self.limits({
            FOO_IMAGE_LIMIT_IDENTIFIER: {
                'soft': {
                    'width': 100,
                    'height': 100
                },
                'hard': {
                    'width': 50,
                    'height': 50,
                }
            },
            BAR_IMAGE_LIMIT_IDENTIFIER: {
                'soft': {
                    'width': 500,
                    'height': 500
                },
                'hard': {
                    'width': 250,
                    'height': 250,
                }
            }
        })

        # Soft limit width
        self.assertTrue(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER, width=200))
        self.assertFalse(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER, width=70))

        # Hard limit width
        self.assertTrue(limits.validate('hard', FOO_IMAGE_LIMIT_IDENTIFIER, width=70))
        self.assertFalse(limits.validate('hard', FOO_IMAGE_LIMIT_IDENTIFIER, width=30))

        # Soft limit height
        self.assertTrue(limits.validate('soft', BAR_IMAGE_LIMIT_IDENTIFIER, height=600))
        self.assertFalse(limits.validate('soft', BAR_IMAGE_LIMIT_IDENTIFIER, height=400))

        # Hard limit height
        self.assertTrue(limits.validate('hard', BAR_IMAGE_LIMIT_IDENTIFIER, height=300))
        self.assertFalse(limits.validate('hard', BAR_IMAGE_LIMIT_IDENTIFIER, height=200))

        # Soft limit width and height
        self.assertTrue(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER,
                                        width=200, height=200))
        self.assertFalse(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER,
                                         width=70, height=70))
        self.assertFalse(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER,
                                         width=200, height=70))
        self.assertFalse(limits.validate('soft', FOO_IMAGE_LIMIT_IDENTIFIER,
                                         width=70, height=200))

        # Hard limit width and height
        self.assertTrue(limits.validate('soft', BAR_IMAGE_LIMIT_IDENTIFIER,
                                        width=600, height=600))
        self.assertFalse(limits.validate('soft', BAR_IMAGE_LIMIT_IDENTIFIER,
                                         width=70, height=70))
        self.assertFalse(limits.validate('soft', BAR_IMAGE_LIMIT_IDENTIFIER,
                                         width=600, height=70))
        self.assertFalse(limits.validate('soft', BAR_IMAGE_LIMIT_IDENTIFIER,
                                         width=70, height=600))

    def test_get_limits_for_returns_limits(self):
        limits = self.limits({
            FOO_IMAGE_LIMIT_IDENTIFIER: {
                'soft': {
                    'width': 100,
                    'height': 100
                },
                'hard': {
                    'width': 50,
                    'height': 75,
                }
            }
        })

        self.assertEqual(
            {'width': 0, 'height': 0},
            limits.get_limits_for('hard', BAR_IMAGE_LIMIT_IDENTIFIER))

        self.assertDictEqual(
            {'width': 50, 'height': 75},
            limits.get_limits_for('hard', FOO_IMAGE_LIMIT_IDENTIFIER))

    def test_get_all_limits_for_returns_all_registered_limits(self):
        limits = self.limits({
            FOO_IMAGE_LIMIT_IDENTIFIER: {
                'soft': {
                    'width': 100,
                },
                'hard': {
                    'width': 50,
                    'height': 75,
                }
            }
        })

        self.assertDictEqual({
            'hard': {'width': 50, 'height': 75},
            'soft': {'width': 100, 'height': 0}
            },
            limits.get_all_limits_for(FOO_IMAGE_LIMIT_IDENTIFIER)
        )


class TestImageLimits(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_CONTENT_TESTING

    def image_limits(self, config, context=None):
        image_limits = IImageLimits(context)
        image_limits.limits.limit_configuration = config

        return image_limits

    def test_validate_limits(self):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        image_limits = self.image_limits({
            block.portal_type: {
                'soft': {
                    'width': block.image._width + 100,
                },
                'hard': {
                    'width': block.image._width - 100,
                }
            },
        }, block)

        # Soft limit width
        self.assertFalse(image_limits.validate('soft'))

        # Hard limit width
        self.assertTrue(image_limits.validate('hard'))

    def test_get_limits_for_returns_limits(self):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        image_limits = self.image_limits({
            block.portal_type: {
                'soft': {
                    'width': 100,
                }
            }
        }, block)

        self.assertEqual(
            {'width': 100, 'height': 0},
            image_limits.get_limits_for('soft'))

    def test_get_all_limits_for_returns_all_registered_limits(self):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        image_limits = self.image_limits({
            block.portal_type: {
                'soft': {
                    'width': 100,
                }
            }
        }, block)

        self.assertDictEqual({
            'hard': {'width': 0, 'height': 0},
            'soft': {'width': 100, 'height': 0}
            },
            image_limits.get_all_limits()
        )

    def test_has_low_quality_image_returns_true_if_soft_limit_not_satisfied(self):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())
        image_limits = self.image_limits({
            block.portal_type: {
                'soft': {
                    'width': block.image._width + 100,
                },
            }
        }, block)

        self.assertTrue(image_limits.has_low_quality_image())

    def test_has_low_quality_image_returns_false_if_soft_limit_is_satisfied(self):
        page = create(Builder('sl content page'))
        block = create(Builder('sl textblock').within(page).with_dummy_image())

        image_limits = self.image_limits({
            block.portal_type: {
                'soft': {
                    'width': block.image._width < 100,
                },
            }
        }, block)

        self.assertFalse(image_limits.has_low_quality_image())
