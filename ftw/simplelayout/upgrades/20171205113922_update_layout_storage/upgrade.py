from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.upgrade import UpgradeStep


class UpdateLayoutStorage(UpgradeStep):
    """Update layout storage.
    """

    def __call__(self):
        self.install_upgrade_profile()
        for page in self.objects(
                {'object_provides': ISimplelayout.__identifier__},
                'Update attribute in which the layout is stored.'):
            page_config = IPageConfiguration(page)
            state = page_config.load()

            for slot in state.values():
                for layout in slot:
                    if 'config' in layout:
                        self.move_layout_config(layout['config'])

            page_config.store(state)

    def move_layout_config(self, config):
        if 'golden_ratio' in config:
            config['layout'] = 'golden-ratio'
            del config['golden_ratio']
        if 'layout13' in config:
            config['layout'] = 'layout13'
            del config['layout13']
        if 'layout121' in config:
            config['layout'] = 'layout121'
            del config['layout121']
        if 'layout112' in config:
            config['layout'] = 'layout112'
            del config['layout112']

