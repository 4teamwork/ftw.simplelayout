from copy import deepcopy
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutContainerConfig
from operator import itemgetter
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from zExceptions import Unauthorized
from zope.annotation import IAnnotations
from zope.component import queryMultiAdapter
from zope.interface import implements


SL_ANNOTATION_KEY = 'ftw.simplelayout.pageconfiguration'
BLOCK_ANNOTATION_KEY = 'ftw.simplelayout.blockconfiguration'


def make_resursive_persistent(conf):
    """Convert the given layout configuration to a rows/columns/blocks
       mapping.
    """
    # TODO: validate data

    def persist(data):
        if isinstance(data, dict):
            data = PersistentMapping(data)

            for key, value in data.items():
                data[key] = persist(value)

        elif isinstance(data, list):
            return PersistentList(map(persist, data))

        else:
            # Usually we got basestrings, or integer here, so do nothing.
            pass

        return data

    return persist(conf)


class PageConfiguration(object):
    """Adapter for storing simplelayout page configuration.
    """
    implements(IPageConfiguration)

    def __init__(self, context):
        self.context = context

    def store(self, conf):
        self.check_permission(conf)
        annotations = IAnnotations(self.context)
        annotations[SL_ANNOTATION_KEY] = make_resursive_persistent(conf)

    def load(self):
        annotations = IAnnotations(self.context)
        return deepcopy(annotations.setdefault(SL_ANNOTATION_KEY,
                                               self._default_page_config()))

    def check_permission(self, new_state):
        def flatten(payload):
            return [(name, map(len, map(itemgetter('cols'), data)))
                    for name, data in payload.items()]

        if not api.user.has_permission('ftw.simplelayout: Change Layouts',
                                       obj=self.context):
            # The user does not have the permission to manipulate the
            # structure. But the new configuration is serialized from the DOM
            # So we need to check if the user has manipulated the DOM by
            # himself. This is done by flatten the actual and the new state
            # without the block informations.
            flatten_old = flatten(self.load())
            flatten_new = flatten(new_state)

            if flatten_old != flatten_new:
                raise Unauthorized()

    def _default_page_config(self):
        """Returns a default page config"""
        adapter = queryMultiAdapter((self.context, self.context.REQUEST),
                                    ISimplelayoutContainerConfig)

        if adapter is not None:
            layout = adapter.default_page_layout()
            if layout is not None:
                return layout

        return {}


class BlockConfiguration(object):
    """Adapter for storing block configuration.
    """
    implements(IBlockConfiguration)

    def __init__(self, context):
        self.context = context

    def store(self, data):
        annotations = IAnnotations(self.context)
        annotations[BLOCK_ANNOTATION_KEY] = PersistentMapping(data)

    def load(self):
        annotations = IAnnotations(self.context)
        return annotations.setdefault(BLOCK_ANNOTATION_KEY,
                                      PersistentMapping())
