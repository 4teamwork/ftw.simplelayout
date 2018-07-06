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
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides


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

    def is_baseline(self):
        """Returns whether the adapted object is a baseline.
        """
        return IBaseline.providedBy(self.context)

    def is_working_copy(self):
        """Returns whether the adapted object is a working copy.
        """
        return IWorkingCopy.providedBy(self.context)

    def get_baseline(self):
        """When the adapted object is a working copy, the baseline is returned, otherwise None.
        """
        if self.is_working_copy():
            return uuidToObject(self.context._baseline)

    def get_working_copies(self):
        """When the adapted object is a baseline, a list of working copies is returned.
        """
        if not self.is_baseline():
            return None

        return map(uuidToObject, self.context._working_copies)

    def create_working_copy(self, target_container):
        """Make a working copy of the adapted context into the given target container.
        """
        working_copy = self._create_clone(self.context, target_container)
        alsoProvides(self.context, IBaseline)
        alsoProvides(working_copy, IWorkingCopy)
        self._link(self.context, working_copy)
        return working_copy

    def discard_working_copy(self):
        """When the adapted context is the working copy, this method discards the
        working copy by deleting it.
        """
        if not self.is_working_copy():
            raise ValueError('Adapted context must be a working copy.')

        baseline = self.get_baseline()
        working_copy = self.context

        self._unlink(baseline, working_copy)
        noLongerProvides(baseline, IBaseline)
        aq_parent(aq_inner(working_copy)).manage_delObjects([working_copy.getId()])

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

    def _link(self, baseline, working_copy):
        if not hasattr(baseline, '_working_copies'):
            baseline._working_copies = PersistentList()

        baseline._working_copies.append(IUUID(working_copy))
        working_copy._baseline = IUUID(baseline)

    def _unlink(self, baseline, working_copy):
        del working_copy._baseline
        baseline._working_copies.remove(IUUID(working_copy))
