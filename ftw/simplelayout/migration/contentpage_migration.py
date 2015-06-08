from ftw.simplelayout.interfaces import IPageConfiguration
from ftw.simplelayout.migration.migration_helpers import migrate
from plone.app.contenttypes.migration.migration import ATCTFolderMigrator
from simplelayout.base.interfaces import IAdditionalListingEnabled
from simplelayout.base.interfaces import ISimplelayoutTwoColumnOneOnTopView
from simplelayout.base.interfaces import ISimplelayoutTwoColumnView
from simplelayout.base.interfaces import ISimplelayoutView


class FtwContenPageMigrator(ATCTFolderMigrator):

    src_portal_type = 'ContentPage'
    src_meta_type = 'ContentPage'
    dst_portal_type = 'ftw.simplelayout.ContentPage'
    dst_meta_type = None  # not used

    def migrate_prepare_page_state(self):
        config = IPageConfiguration(self.new)
        page_config = config.load()

        if ISimplelayoutView.providedBy(self.old):
            # On container, one layout and one column
            # this happens in 99% of all pages
            page_config = {
                "default": [
                    {"cols": [
                        {"blocks": []}]
                     }]}
        elif ISimplelayoutTwoColumnView.providedBy(self.old):
            page_config = {
                "default": [
                    {"cols": [
                        {"blocks": []},
                        {"blocks": []}]
                     }]}
        elif ISimplelayoutTwoColumnOneOnTopView.providedBy(self.old):
            page_config = {
                "default": [
                    {"cols": [
                        {"blocks": []}]},
                    {"cols": [
                        {"blocks": []},
                        {"blocks": []}]
                     }]}

        if IAdditionalListingEnabled.providedBy(self.old):
            # This adds a new one column simplelayout container
            page_config['additional'] = [
                {"cols": [{"blocks": []}]}]

        config.store(page_config)


def contentpage_migrator(portal):
    return migrate(portal, FtwContenPageMigrator)
