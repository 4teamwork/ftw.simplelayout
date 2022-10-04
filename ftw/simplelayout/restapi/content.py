from ftw.simplelayout.interfaces import IBlockConfiguration
from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.interfaces import ISimplelayout
from ftw.simplelayout.interfaces import ISimplelayoutBlock
from ftw.simplelayout.interfaces import ISimplelayoutLayer
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone import api
from plone.dexterity.interfaces import IDexterityContainer
from plone.restapi.batching import HypermediaBatch
from plone.restapi.deserializer import boolean_value
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.dxcontent import SerializeFolderToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from plone.restapi.serializer.site import SerializeSiteRootToJson
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
import json
import logging


LOG = logging.getLogger(__name__)


class PersistenceDecoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, PersistentMapping):
            return dict(obj)
        elif isinstance(obj, PersistentList):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


def _sl_blocks_query(context):
    return {
        'path': {'depth': 1, 'query': '/'.join(context.getPhysicalPath())},
        'object_provides': ISimplelayoutBlock.__identifier__,
    }


def enrich_with_simplelayout(context, result):

    result['simplelayout'] = json.loads(json.dumps(
        IPageConfiguration(context).load(),
        cls=PersistenceDecoder)
    )

    catalog = api.portal.get_tool('portal_catalog')
    brains = catalog(_sl_blocks_query(context))

    blocks = []
    for item in brains:
        try:
            obj = item.getObject()
        except KeyError:
            LOG.warning(
                "Brain getObject error: {} doesn't exist anymore".format(
                    item.getPath()
                )
            )
            continue

        block_data = getMultiAdapter((obj, context.REQUEST), ISerializeToJson)(
            include_items=False
        )
        blocks.append(block_data)

    result['slblocks'] = {block['UID']: block for block in blocks}


@implementer(ISerializeToJson)
@adapter(ISimplelayout, Interface)
class SimplelayoutSerializer(SerializeToJson):
    def _build_query(self):
        path = "/".join(self.context.getPhysicalPath())
        query = {
            "path": {"depth": 1, "query": path},
            "sort_on": "getObjPositionInParent",
        }
        return query

    def __call__(self, version=None, include_items=True):
        folder_metadata = super(SimplelayoutSerializer, self).__call__(version=version)

        folder_metadata.update({"is_folderish": True})
        result = folder_metadata

        enrich_with_simplelayout(self.context, result)

        include_items_request = self.request.form.get("include_items", include_items)
        include_items_request = boolean_value(include_items_request)

        # Only include items if request and kwarg really want it to inlcude.
        # This prevents a recursive inclusion of all items (tree), since
        # the ISerializeToJson of brains calls the serializer with the argument
        # include_items=False. But so far this go ignored if the request parameter
        # include_items was present.
        if include_items and include_items_request:
            query = self._build_query()

            catalog = getToolByName(self.context, "portal_catalog")
            brains = catalog(query)

            batch = HypermediaBatch(self.request, brains)

            result["items_total"] = batch.items_total
            if batch.links:
                result["batching"] = batch.links

            if "fullobjects" in list(self.request.form):
                result["items"] = getMultiAdapter(
                    (brains, self.request), ISerializeToJson
                )(fullobjects=True)["items"]
            else:
                result["items"] = [
                    getMultiAdapter((brain, self.request), ISerializeToJsonSummary)()
                    for brain in batch
                ]
        return result


@implementer(ISerializeToJson)
@adapter(IPloneSiteRoot, ISimplelayoutLayer)
class SimplelayoutSerializeSiteRootToJson(SerializeSiteRootToJson):
    def __call__(self, version=None):
        result = super(SimplelayoutSerializeSiteRootToJson, self).__call__(version=version)
        enrich_with_simplelayout(self.context, result)
        return result


@implementer(ISerializeToJson)
@adapter(ISimplelayoutBlock, Interface)
class SimplelayoutBlockSerializeToJson(SerializeToJson):
    def __call__(self, version=None, include_items=True):
        result = super(SimplelayoutBlockSerializeToJson, self).__call__(version=version, include_items=include_items)

        result['block-configuration'] = json.loads(json.dumps(
            IBlockConfiguration(self.context).load(),
            cls=PersistenceDecoder)
        )

        if IDexterityContainer.providedBy(self.context):
            result['items'] = SerializeFolderToJson(self.context, self.request)()['items']

        return result
