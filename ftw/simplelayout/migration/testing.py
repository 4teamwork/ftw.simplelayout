from ftw.simplelayout.tests import builders
from ftw.contentpage.tests import builders
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.testing import z2
from zope.configuration import xmlconfig
from ftw.contentpage.testing import FtwContentPageLayer


class FtwSimplelayoutMigrationLayer(FtwContentPageLayer):

    def setUpZope(self, app, configurationContext):
        super(FtwSimplelayoutMigrationLayer, self).setUpZope(
            app,
            configurationContext)

        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.simplelayout
        xmlconfig.file('configure.zcml', ftw.simplelayout,
                       context=configurationContext)
        z2.installProduct(app, 'ftw.simplelayout')

    def setUpPloneSite(self, portal):
        super(FtwSimplelayoutMigrationLayer, self).setUpPloneSite(portal)
        applyProfile(portal, 'ftw.simplelayout:default')


FTW_SIMPLELAYOUT_MIGRATION_FIXTURE = FtwSimplelayoutMigrationLayer()
FTW_SIMPLELAYOUT_MIGRATON_TESTING = IntegrationTesting(
    bases=(FTW_SIMPLELAYOUT_MIGRATION_FIXTURE,),
    name="FtwSimplelayout:Migration")
