from collections import OrderedDict
from zope.i18n import translate
from ftw.simplelayout import _
from ftw.simplelayout.interfaces import ISimplelayoutActions
from zope.interface import implements


class DefaultActions(object):

    implements(ISimplelayoutActions)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.actions = OrderedDict(self.specific_actions().items() +
                                   self.default_actions().items())

    def default_actions(self):
        """Contains default action - move, edit, delete"""
        return OrderedDict([
            ('move', {
                'class': 'move sl-icon-move',
                'title': translate(
                    _(u'label_move_block', default='Move block'),
                    context=self.request),
            }),
            ('edit', {
                'class': 'edit sl-icon-edit',
                'title': translate(
                    _(u'label_edit_block', default='Edit block'),
                    context=self.request),
                'href': self.context.absolute_url() + '/sl-ajax-edit-block-view'
            }),
            ('delete', {
                'class': 'delete sl-icon-delete',
                'title': translate(
                    _(u'label:delete_block', default='Delete block'),
                    context=self.request),
                'href': self.context.absolute_url() + '/sl-ajax-delete-blocks-view'
            })
        ])

    def specific_actions(self):
        return OrderedDict()
