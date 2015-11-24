from ftw.simplelayout.handlers import unwrap_persistence
from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping


class TestUnwrapPersistance(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def test_unwrap_persistance(self):
        config = PersistentMapping(
            {'default': PersistentList([
                PersistentMapping({'cols': "columns"}),
                PersistentMapping({'cols': 'columns'})]
                )})

        unwrapped_config = unwrap_persistence(config)

        self.assert_unwrapped_persistence(unwrapped_config)

    def test_unwrap_partial_persistance_with_list(self):
        config = PersistentMapping(
            {'default': list([
                PersistentMapping({'cols': "columns"}),
                PersistentMapping({'cols': 'columns'})])})

        unwrapped_config = unwrap_persistence(config)

        self.assert_unwrapped_persistence(unwrapped_config)

    def test_unwrap_partial_persistance_with_dict(self):
        config = dict(
            {'default': PersistentList([
                PersistentMapping({'cols': "columns"}),
                PersistentMapping({'cols': 'columns'})])})

        unwrapped_config = unwrap_persistence(config)

        self.assert_unwrapped_persistence(unwrapped_config)

    def test_unwrap_partial_persistance_with_tuple(self):
        config = PersistentMapping(
            {'default': tuple([
                PersistentMapping({'cols': "columns"}),
                PersistentMapping({'cols': 'columns'})])})

        unwrapped_config = unwrap_persistence(config)

        self.assert_unwrapped_persistence(unwrapped_config)

    def test_unwrap_partial_persistance_with_set(self):
        config = PersistentMapping(
            {'default': set(['value1', 'value2'])})

        unwrapped_config = unwrap_persistence(config)

        self.assert_unwrapped_persistence(unwrapped_config)
