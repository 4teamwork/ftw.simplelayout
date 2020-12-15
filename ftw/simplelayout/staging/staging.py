from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from BTrees.OOBTree import OOBTree
from contextlib import contextmanager
from copy import deepcopy
from DateTime import DateTime
from datetime import datetime
from ftw.simplelayout.configuration import columns_in_config
from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.properties import BLOCK_PROPERTIES_KEY
from ftw.simplelayout.staging.interfaces import IBaseline
from ftw.simplelayout.staging.interfaces import IStaging
from ftw.simplelayout.staging.interfaces import IWorkingCopy
from ftw.simplelayout.utils import unrestricted_uuidToObject
from operator import methodcaller
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.app.uuid.utils import uuidToObject
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from plone.uuid.interfaces import IUUID
from Products.Archetypes.interfaces import IBaseContent
from zope.annotation.interfaces import IAnnotations
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import noLongerProvides
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from zope.schema import getFieldsInOrder
import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.event')
except pkg_resources.DistributionNotFound:
    EVENT_SUPPORT = False
else:
    EVENT_SUPPORT = True
    from plone.app.event.dx.behaviors import EventBasic


try:
    pkg_resources.get_distribution('ftw.trash')
except pkg_resources.DistributionNotFound:
    FTW_TRASH_SUPPORT = False
else:
    FTW_TRASH_SUPPORT = True
    from ftw.trash.interfaces import ITrashed


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

    IGNORED_AT_FIELDS = (
        'id',
        'creation_date',
        'modification_date',
    )

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
        """When the adapted object is a working copy, the baseline is returned,
        otherwise None.
        """
        if self.is_working_copy():
            return uuidToObject(self.context._baseline)

    def get_working_copies(self):
        """When the adapted object is a baseline, a list of working copies is returned.
        """
        if not self.is_baseline():
            return None

        return map(unrestricted_uuidToObject, self.context._working_copies)

    def create_working_copy(self, target_container):
        """Make a working copy of the adapted context into the given target container.
        """
        working_copy = self._create_clone(self.context, target_container)
        self._remove_auto_generated_children(self.context, working_copy)
        alsoProvides(self.context, IBaseline)
        alsoProvides(working_copy, IWorkingCopy)
        self._link(self.context, working_copy)
        uuid_map = self._map_uuids(self.context, working_copy)
        self._update_internal_links_recursively(working_copy, uuid_map)
        return working_copy

    def apply_working_copy(self):
        """Apply the changes of the working copy back to the baseline and remove
        the working copy.
        """
        if not self.is_working_copy():
            raise ValueError('Adapted context must be a working copy.')

        baseline = self.get_baseline()
        working_copy = self.context
        uuid_map = self._apply_children(working_copy, baseline,
                                        condition=self.is_child_integrated)
        self._update_internal_links_recursively(baseline, uuid_map,
                                                condition=self.is_child_integrated)

        self._update_simplelayout_page_state(working_copy, baseline, uuid_map)
        self._unlink_and_delete_working_copy(baseline, working_copy)

    def discard_working_copy(self):
        """When the adapted context is the working copy, this method discards the
        working copy by deleting it.
        """
        if not self.is_working_copy():
            raise ValueError('Adapted context must be a working copy.')

        baseline = self.get_baseline()
        working_copy = self.context
        self._unlink_and_delete_working_copy(baseline, working_copy)

    def is_child_integrated(self, obj):
        """Condition for deciding whether a child is "integrated" or not.
        By "integrated" it's meant that the child is considered part of the content
        and thus is copyied / applied along with the staged container.
        In simplelayout this applies to simplelayout blocks by defualt.
        """
        return ISimplelayoutBlock.providedBy(obj)

    def _create_clone(self, obj, target_container):
        """When cloning an object, we want to make sure that we do not clone
        child objects which we will not use later.
        This is important as we may make a working copy of a root node which
        contains very large structures.
        """
        source_container = aq_parent(aq_inner(obj))
        obj = aq_base(obj)
        with self._cleanup_filter_tree(obj), self._cleanup_filter_order(obj):
            clipboard = source_container.manage_copyObjects([obj.getId()])
            copy_info, = target_container.manage_pasteObjects(clipboard)
        working_copy = target_container.get(copy_info['new_id'])
        working_copy.creation_date = DateTime()
        working_copy.reindexObject(idxs=['created'])
        return working_copy

    def _remove_auto_generated_children(self, baseline, working_copy):
        """When creating a working copy, we do not want have additionaly auto generated
        children, which may be auto generated by subscribers.
        Reasons:
        - It will not work later in the staging process; it will cause an exception.
        - Each time we create a working copy we would end up with one child more.
        """
        baseline_children = set(baseline.objectIds())
        working_copy_children = set(working_copy.objectIds())
        children_to_delete = list(working_copy_children - baseline_children)

        if hasattr(working_copy, 'manage_immediatelyDeleteObjects'):
            # When ftw.trash is installed, immediately delete the working copy.
            working_copy.manage_immediatelyDeleteObjects(children_to_delete)
        else:
            working_copy.manage_delObjects(children_to_delete)

    @contextmanager
    def _cleanup_filter_tree(self, obj):
        """Filter the child objects of the ``obj`` so only children considered
        as "integrated" are beeing kept.
        The context manager restores on exit.
        """
        original = obj._tree
        obj._tree = OOBTree({key: value for (key, value) in obj._tree.items()
                             if self.is_child_integrated(value)})
        original_count = obj._count()
        obj._count.set(len(obj._tree))

        # Revert the tree patch within a IObjectCopiedEvent subscriber in order
        # to revert right after inserting the working copy object but before
        # other event subscribers are triggered.
        # One regular paste subscriber is from plone.app.linkitegrity, verifying
        # the relations. If we have relations with a subpage as target in our
        # pasted content, it will fail when the tree change is not reverted since
        # the subpage is then not reachable at all.
        def object_copied_subscriber(event):
            if event.original == obj:
                revert()

        handler_args = (object_copied_subscriber, (IObjectCopiedEvent,))

        def revert():
            if getattr(original, '_p_jar', object()) != getattr(obj, '_p_jar', object()):
                # The handler is registered for all thread; this is a call from another
                # thread, so ignore it.
                return

            if obj._tree == original:
                # revert() usually is called twice; only reset once.
                return
            getGlobalSiteManager().unregisterHandler(*handler_args)
            obj._tree = original
            obj._count.set(original_count)

        getGlobalSiteManager().registerHandler(*handler_args)
        try:
            yield
        finally:
            revert()

    @contextmanager
    def _cleanup_filter_order(self, obj):
        """Cleanup order according to already cleaned up object tree.
        The context manager restores on exit.
        """
        annotations = IAnnotations(obj)
        annkey = 'plone.folder.ordered.order'
        if annkey in annotations:
            original = annotations[annkey]
            annotations[annkey] = PersistentList(
                [key for key in original if key in obj._tree])
        try:
            yield
        finally:
            if annkey in annotations:
                annotations[annkey] = original

    def _map_uuids(self, baseline, working_copy):
        """Map uuids of baseline objects and working copy objects.
        The uuid of the baseline object is stored on the working copy object,
        recursively.
        The method returns a map from baseline objects to their working copy objects.
        """
        baseline_to_workingcopy = {}

        def handle(baseline_obj, working_copy_obj):
            baseline_to_workingcopy[IUUID(baseline_obj)] = IUUID(working_copy_obj)
            working_copy_obj._baseline_obj_uuid = IUUID(baseline_obj)
            for name in working_copy_obj.objectIds():
                handle(baseline_obj[name], working_copy_obj[name])

        handle(baseline, working_copy)
        return baseline_to_workingcopy

    def _link(self, baseline, working_copy):
        if not hasattr(baseline, '_working_copies'):
            baseline._working_copies = PersistentList()

        baseline._working_copies.append(IUUID(working_copy))
        working_copy._baseline = IUUID(baseline)

    def _unlink(self, baseline, working_copy):
        del working_copy._baseline
        baseline._working_copies.remove(IUUID(working_copy))

    def _unlink_and_delete_working_copy(self, baseline, working_copy):
        self._unlink(baseline, working_copy)
        noLongerProvides(baseline, IBaseline)
        noLongerProvides(working_copy, IWorkingCopy)

        parent = aq_parent(aq_inner(working_copy))
        if hasattr(parent, 'manage_immediatelyDeleteObjects'):
            # When ftw.trash is installed, immediately delete the working copy.
            parent.manage_immediatelyDeleteObjects([working_copy.getId()])
        else:
            parent.manage_delObjects([working_copy.getId()])

    def _apply_children(self, source, target, condition=None, uuid_map=None):
        uuid_map = uuid_map or {}
        uuid_map[IUUID(source)] = IUUID(target)
        target_children_map = {IUUID(obj): obj for obj in self._get_children(target, condition)}
        source_ids = source.objectIds()
        self._copy_field_values(source, target)
        self._purge_scales(target)
        self._update_simplelayout_block_state(source, target)

        for source_child in self._get_children(source, condition):
            target_uid = getattr(source_child, '_baseline_obj_uuid', None)
            if target_uid in target_children_map:
                target_child = target_children_map.pop(target_uid)
                self._apply_children(source_child, target_child, uuid_map=uuid_map)
            else:
                target_child = self._move_new_obj(source_child, target)
                uuid_map[IUUID(source_child)] = IUUID(target_child)

        target.moveObjectsToTop(source_ids)
        target.manage_delObjects(map(methodcaller('getId'), target_children_map.values()))
        target.reindexObject()
        return uuid_map

    def _update_simplelayout_page_state(self, working_copy, baseline, uuid_map):
        """Copy the simplelayout page state from the working copy to the baseline
        and change the working copy block UUIDs to the existing baseline block UUIDs
        unless new blocks are added.
        """
        config = IPageConfiguration(working_copy).load()
        for column in columns_in_config(config):
            for block in column['blocks']:
                if block['uid'] in uuid_map:
                    block['uid'] = uuid_map[block['uid']]

        IPageConfiguration(baseline).store(config)

    def _update_simplelayout_block_state(self, source, target):
        """Copy the simplelayout block state from the source block to the target block.
        """
        source_configuration = IBlockConfiguration(source, None)
        if source_configuration:
            config = deepcopy(source_configuration.load())
            IBlockConfiguration(target).store(config)

        source_ann = IAnnotations(source)
        target_ann = IAnnotations(target)
        if BLOCK_PROPERTIES_KEY in source_ann:
            target_ann[BLOCK_PROPERTIES_KEY] = PersistentMapping(
                source_ann[BLOCK_PROPERTIES_KEY])
        else:
            target_ann.pop(BLOCK_PROPERTIES_KEY, None)

    def _update_internal_links_recursively(self, obj, uuid_map, condition=None):
        if IDexterityContent.providedBy(obj):
            self._update_internal_links_DX(obj, uuid_map)
        for child in self._get_children(obj, condition):
            self._update_internal_links_recursively(child, uuid_map)

    def _update_internal_links_DX(self, obj, uuid_map):
        for name, field, schemata in self._iter_fields(obj.portal_type):
            if not IRichText.providedBy(field):
                continue

            storage = schemata(obj)
            ori_text = getattr(storage, name)
            if not ori_text:
                continue

            new_text = self._replace_uids_in_html(ori_text.raw, uuid_map)
            if new_text == ori_text.raw:
                continue

            setattr(storage, name, RichTextValue(new_text,
                                                 mimeType=ori_text._mimeType,
                                                 outputMimeType=ori_text._outputMimeType))

    def _replace_uids_in_html(self, html, uuid_map):
        for from_uuid, to_uuid in uuid_map.items():
            html = html.replace(from_uuid, to_uuid)
        return html

    def _copy_field_values(self, source, target):
        """Copy all fields values from "source" to "target".
        """
        if type(source) != type(target):
            raise ValueError('Objects have differing classes ({!r} != {!r})'.format(
                type(source), type(target)))

        if IDexterityContent.providedBy(source):
            return self._copy_dx_field_values(source, target)

        if IBaseContent.providedBy(source):
            return self._copy_at_field_values(source, target)

        raise ValueError('Unsupported object type {!r}, neither AT nor DX.'.format(
            source))

    def _copy_dx_field_values(self, source, target):
        for name, field, schemata in self._iter_fields(source.portal_type):
            source_storage = schemata(source)
            target_storage = schemata(target)
            value = getattr(source_storage, name)

            if EVENT_SUPPORT and isinstance(target_storage, EventBasic) and \
               isinstance(value, datetime):
                value = getattr(source, name)
            elif isinstance(value, str):
                value = value.decode('utf-8')

            setattr(target_storage, field.getName(), value)

    def _copy_at_field_values(self, source, target):
        for source_field in source.Schema().values():
            if source_field.__name__ in self.IGNORED_AT_FIELDS:
                continue

            # Re-fetch the field from the target schema since source and
            # target schema may vary because of dynamice schema extenders.
            target_field = target.Schema().getField(source_field.__name__)
            value = source_field.getRaw(source)
            target_field.set(target, value)

    def _iter_fields(self, portal_type):
        for schemata in self._iter_schemata_for_protal_type(portal_type):
            for name, field in getFieldsInOrder(schemata):
                if not getattr(field, 'readonly', False):
                    yield (name, field, schemata)

    def _iter_schemata_for_protal_type(self, portal_type):
        fti = getUtility(IDexterityFTI, name=portal_type)
        yield fti.lookupSchema()
        for schema in getAdditionalSchemata(portal_type=portal_type):
            yield schema

    def _move_new_obj(self, obj, new_parent):
        clipboard = aq_parent(aq_inner(obj)).manage_cutObjects([obj.getId()])
        info = new_parent.manage_pasteObjects(clipboard)
        return new_parent.get(info[0]['new_id'])

    def _purge_scales(self, obj):
        """When copying value from one object to another, they may include images
        which have scales. In order to make sure that we do not use old caches,
        we are purging the complete scaling cache so that the scales will be
        regenerated when needed.
        """
        IAnnotations(obj).pop('plone.scale', None)

    def _get_children(self, folder, filter_condition=None):
        """Return the children of a container, supporting the trash and an arbitrary
        filter condition.
        """
        children = filter(filter_condition, folder.objectValues())

        if FTW_TRASH_SUPPORT:
            children = filter(lambda item: not ITrashed.providedBy(item), children)

        return children
