from ftw.simplelayout.aliasblock.contents.interfaces import IAliasBlock
from plone import api
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter


def geo_settings_installed():
    version = api.portal.get().portal_setup.getLastVersionForProfile('collective.geo.settings:default')
    return version != 'unknown'



class AliasBlockFormViewlet(ViewletBase):
    index = ViewPageTemplateFile('templates/aliasblock_form_viewlet.pt')

    def update(self):
        super(AliasBlockFormViewlet, self).update()

        is_aliasblock = IAliasBlock.providedBy(self.context)
        is_aliasblock_add_form = self.view.__name__ == 'ftw.simplelayout.AliasBlock'

        self.do_render_mapwidget = (is_aliasblock or is_aliasblock_add_form) and geo_settings_installed()
