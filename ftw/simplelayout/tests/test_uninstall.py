from ftw.testing import IS_PLONE_5
from ftw.testing.genericsetup import GenericSetupUninstallMixin
from ftw.testing.genericsetup import apply_generic_setup_layer
from unittest2 import TestCase
from unittest2 import skipIf
from unittest2 import skipUnless


@apply_generic_setup_layer
@skipIf(IS_PLONE_5, 'The map block is not available for Plone 5.')
class TestGenericSetupUninstallMapBlock(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.simplelayout.mapblock'


@apply_generic_setup_layer
@skipIf(IS_PLONE_5, 'Test the uninstall profile for Plone 4')
class TestGenericSetupUninstallContentTypes(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.simplelayout.contenttypes'


@apply_generic_setup_layer
@skipUnless(IS_PLONE_5, 'Test the uninstall profile for Plone 5')
class TestGenericSetupUninstallContentTypes(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.simplelayout.contenttypes'

    # Plone 5 does not support "propertiestool.xml" anymore.
    skip_files = ('propertiestool.xml',)
