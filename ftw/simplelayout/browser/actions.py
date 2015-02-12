from collections import OrderedDict
from ftw.simplelayout.interfaces import ISimplelayoutActions
from zope.interface import implements


class DefaultActions(object):

    implements(ISimplelayoutActions)

    def __init__(self, context, request):
        self.context = context
        self.request = request

        self.actions = self.default_actions()
        if self.specific_actions():
            self.actions.update(self.specific_actions())

    def default_actions(self):
        """Contains default action - move, edit, delete"""
        return OrderedDict(move={'class': 'Move icon-move',
                                 'title': 'Move block',
                                 },
                           edit={'class': 'Edit icon-edit',
                                 'title': 'Edit block',
                                 'href': './block-edit'
                                 },
                           delete={'class': 'Delete icon-delete',
                                   'title': 'Delete block',
                                   'href': './sl-ajax-delete-blocks-view'
                                   })

    def specific_actions(self):
        return None
