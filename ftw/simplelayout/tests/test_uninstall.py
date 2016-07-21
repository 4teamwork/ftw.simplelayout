from ftw.testing.genericsetup import GenericSetupUninstallMixin
from ftw.testing.genericsetup import apply_generic_setup_layer
from unittest2 import TestCase


@apply_generic_setup_layer
class TestGenericSetupUninstallMapBlock(TestCase, GenericSetupUninstallMixin):
    package = 'ftw.simplelayout.mapblock'
