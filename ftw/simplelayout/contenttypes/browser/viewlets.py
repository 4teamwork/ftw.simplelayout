from Acquisition import aq_inner
from operator import attrgetter
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds


class MediaFolderViewlet(ViewletBase):
    index = ViewPageTemplateFile("templates/viewlet.pt")

    def update(self):
        super(MediaFolderViewlet, self).update()
        self.listingblocks = self.get_referenced_listingblocks()

    def _get_dx_brefs_for(self):
        catalog = getUtility(ICatalog)
        obj_intid = getUtility(IIntIds).getId(aq_inner(self.context))
        relations = catalog.findRelations({'to_id': obj_intid})
        return map(attrgetter('from_object'), relations)

    def get_referenced_listingblocks(self):
        objs = self._get_dx_brefs_for()
        objs = filter(lambda item: bool(item), objs)
        result = []
        for obj in objs:
            result.append(
                {
                    'title': obj.Title(),
                    'url': obj.aq_parent.absolute_url() + '#' + obj.getId(),
                }
            )
        return result
