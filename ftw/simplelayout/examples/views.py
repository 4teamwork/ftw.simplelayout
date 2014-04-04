from ftw.simplelayout.browser.simplelayout import CONFIG_TEMPLATE
from ftw.simplelayout.browser.simplelayout import SimplelayoutView
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class SimplelayoutTwoSlots(SimplelayoutView):
    """Simplelayout view with two slots"""


class SimplelayoutFourColumns(SimplelayoutView):
    """Simplelayout view with four columns"""

    columns = 4

    def load_default_settings(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISimplelayoutDefaultSettings)

        return CONFIG_TEMPLATE.format(
            **{'columns': self.columns or settings.columns,
               'images': 1,
               'contentwidth': 960,
               'margin_right': settings.margin_right,
               'contentarea': settings.contentarea,
               'editable': str(self.can_modify()).lower()})
