from ftw.simplelayout.staging.interfaces import IStaging
from plone import api
from plone.app.layout.viewlets import common
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class WorkingCopyViewlet(common.PathBarViewlet):
    index = ViewPageTemplateFile('templates/workingcopy_viewlet.pt')

    def render(self):
        return self.index()

    @property
    def owner_name(self):
        owner = self.context.getOwner()
        return owner.getProperty('fullname') or owner.getId()

    @property
    def baseline_url(self):
        baseline = IStaging(self.context).get_baseline()
        return baseline.absolute_url()


class BaselineViewlet(common.PathBarViewlet):
    index = ViewPageTemplateFile('templates/baseline_viewlet.pt')

    def render(self):
        if api.user.is_anonymous():
            return ''
        return self.index()

    def get_working_copies(self):
        return IStaging(self.context).get_working_copies()

    def owner_name(self, working_copy):
        owner = working_copy.getOwner()
        return owner.getProperty('fullname') or owner.getId()
