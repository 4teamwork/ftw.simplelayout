from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.upgrade import UpgradeStep
from operator import methodcaller


class UpdateOrderingOfExistingObjects(UpgradeStep):
    """Update ordering of existing objects.
    """

    def __call__(self):
        self.install_upgrade_profile()
        self.update_ordering()

    def update_ordering(self):
        for page in self.objects(
                {'object_provides': ISimplelayout.__identifier__},
                'Update ordering of simplelayout blocks in pages.'):
            IPageConfiguration(page).update_object_positions()
