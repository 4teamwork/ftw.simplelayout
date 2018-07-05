from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from BTrees.OOBTree import OOBTree
from contextlib import contextmanager
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.staging.interfaces import IBaseline
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.simplelayout.staging.interfaces import IWorkingCopy
from persistent.list import PersistentList
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface


@implementer(IStaging)
@adapter(Interface)
def staging_lookup(context):
    """The staging lookup allows for an easy lookup of the adapter by
    simply using IStaging(context).
    We want the request to be adapted anyway, so that the adapter can be customized
    with a browser layer.
    """
    return getMultiAdapter((context, context.REQUEST), IStaging)


@implementer(IStaging)
@adapter(Interface, Interface)
class Staging(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def create_working_copy(self, target_container):
        """Make a working copy of the adapted context into the given target container.
        """
        working_copy = self._create_clone(self.context, target_container)
        alsoProvides(self.context, IBaseline)
        alsoProvides(working_copy, IWorkingCopy)
        return working_copy

    def _create_clone(self, obj, target_container):
        """When cloning an object, we want to make sure that we do not clone
        child objects which we will not use later.
        This is important as we may make a working copy of a root node which
        contains very large structures.
        """
        source_container = aq_parent(aq_inner(obj))
        obj = aq_base(obj)
        with self._cleanup_filter_tree(obj, ISimplelayoutBlock.providedBy), \
             self._cleanup_filter_order(obj):
            clipboard = source_container.manage_copyObjects([obj.getId()])
            copy_info, = target_container.manage_pasteObjects(clipboard)
        return target_container.get(copy_info['new_id'])

    @contextmanager
    def _cleanup_filter_tree(self, obj, condition):
        """Filter the child objects of the ``obj`` so that ``condition`` is ``True`` for
        each child.
        The context manager restores on exit.
        """
        original = obj._tree
        obj._tree = OOBTree({key: value for (key, value) in obj._tree.items() if condition(value)})
        try:
            yield
        finally:
            obj._tree = original

    @contextmanager
    def _cleanup_filter_order(self, obj):
        """Cleanup order according to already cleaned up object tree.
        The context manager restores on exit.
        """
        annotations = IAnnotations(obj)
        annkey = 'plone.folder.ordered.order'
        if annkey in annotations:
            original = annotations[annkey]
            annotations[annkey] = PersistentList([key for key in original if key in obj._tree])
        try:
            yield
        finally:
            if annkey in annotations:
                annotations[annkey] = original
