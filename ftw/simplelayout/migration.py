"""Migration from ftw.contentpage to ftw.simplelayout.
The migration is not registered / executed automatically.
It must be executed manually from an upgrade step in an upgrade step of the
integration project.

Be aware that pages must be migrated before migrating blocks!

The types of ftw.contentpage are split up into multiple packages:

# ftw.simplelayout:
ContentPage => ftw.simplelayout.ContentPage
ListingBlock => ftw.simplelayout.FileListingBlock
                ftw.simplelayout.GalleryBlock
                ftw.sliderblock.SliderBlock
TextBlock => ftw.simplelayout.TextBlock

# ftw.addressblock
AddressBlock => ftw.addressblock.AddressBlock

# ftw.news
News => ftw.news.News
NewsFolder => ftw.news.NewsFolder

# ftw.events
EventPage => ftw.events.EventPage
EventFolder => ftw.events.EventFolder
"""

from ftw.upgrade import UpgradeStep
from ftw.upgrade.migration import InplaceMigrator

# Some sources will probably be removed after running the migration.
# But if the imports are kept and the sources are removed, the imports
# may raise ImportErrors. We only want to have those ImportErrors when
# we actually need to run the migration.
try:

    from archetypes.schemaextender.extender import CACHE_KEY
    from ftw.file.content.file import File
    from ftw.simplelayout.interfaces import IBlockConfiguration
    from ftw.simplelayout.interfaces import IPageConfiguration
    from ftw.simplelayout.interfaces import ISimplelayoutBlock as INewSLBlock
    from ftw.upgrade.migration import DUBLIN_CORE_IGNORES
    from functools import partial
    from operator import attrgetter
    from plone.app.blob.interfaces import IBlobWrapper
    from plone.app.event.dx.behaviors import IEventBasic
    from plone.dexterity.utils import createContentInContainer
    from plone.dexterity.utils import iterSchemata
    from plone.uuid.interfaces import IUUID
    from simplelayout.base.interfaces import IBlockConfig
    from simplelayout.base.interfaces import ISimpleLayoutBlock
    from simplelayout.base.interfaces import ISimplelayoutTwoColumnOneOnTopView
    from simplelayout.base.interfaces import ISimplelayoutTwoColumnView
    from simplelayout.base.interfaces import ISimplelayoutView
    from simplelayout.base.interfaces import ISlotA
    from simplelayout.base.interfaces import ISlotB
    from simplelayout.base.interfaces import ISlotC
    from simplelayout.base.interfaces import ISlotD
    from simplelayout.portlet.dropzone.interfaces import IPortletColumn
    from simplelayout.portlet.dropzone.interfaces import ISlotBlock
    from zope.component import implementedBy
    from zope.component import providedBy
    from zope.interface import noLongerProvides
    from zope.schema import getFieldsInOrder

except ImportError, IMPORT_ERROR:
    pass
else:
    IMPORT_ERROR = None



class ExampleUpgradeStep(UpgradeStep):
    """This is just an example how an upgrade could be done in an upgrade
    step in the integration package.
    """

    def __call__(self):
        page_migrator = ContentPageMigrator()
        map(page_migrator.migrate_object,
            self.objects({'query': 'ContentPage'}), 'Migrate pages')

        textblock_migrator = TextBlockMigrator()
        map(textblock_migrator.migrate_object,
            self.objects({'query': 'TextBlock'}), 'Migrate text blocks')


LEAD_IMAGE_FIELDS = (
    # Lead image is migrated into text block.
    'image',
    'imageAltText',
    'imageCaption',
    'imageClickable',
)


SL_BLOCK_DEFAULT_IGNORED_FIELDS = (
    'effectiveDate',
    'excludeFromNav',
    'expirationDate',
    'subject',
)


def move_sl_block_into_slot(old_page, new_page, block, slot_name):
    page_configuration = IPageConfiguration(new_page)
    page_state = page_configuration.load()

    # initiate layout if it is in its initial state
    if slot_name == 'default' and page_state == page_configuration._default_page_config():

        # setup different layouts
        if ISimplelayoutTwoColumnView.providedBy(old_page):
            # two columns
            page_state[slot_name] = [
                {'cols': [ {'blocks': []}, {'blocks': []} ]}
            ]

        elif ISimplelayoutTwoColumnOneOnTopView.providedBy(old_page):
            # two columns and a top row
            page_state[slot_name] = [
                {'cols': [{'blocks': []}]},
                {'cols': [ {'blocks': []}, {'blocks': []} ]}
            ]

    if slot_name not in page_state:
        # normal single column layout
        page_state[slot_name] = [{'cols': [{'blocks': []}]}]

    if slot_name == 'default':
        slot = page_state['default']

        # two column layout
        if ISimplelayoutTwoColumnView.providedBy(old_page):
            if ISlotA.providedBy(block):  # left column
                slot[0]['cols'][0]['blocks'].append({'uid': IUUID(block)})
            elif ISlotB.providedBy(block):  # right column
                slot[0]['cols'][1]['blocks'].append({'uid': IUUID(block)})
            else:
                raise ValueError('Block has unused slot in layout.')

        # two columns and a top row layout
        elif ISimplelayoutTwoColumnOneOnTopView.providedBy(old_page):
            if ISlotA.providedBy(block):  # top row
                slot[0]['cols'][0]['blocks'].append({'uid': IUUID(block)})
            elif ISlotB.providedBy(block):  # bottom row, left column
                slot[1]['cols'][0]['blocks'].append({'uid': IUUID(block)})
            elif ISlotC.providedBy(block):  # bottom row, right column
                slot[1]['cols'][1]['blocks'].append({'uid': IUUID(block)})
            else:
                raise ValueError('Block has unused slot in layout.')

        else:
            slot[0]['cols'][0]['blocks'].append({'uid': IUUID(block)})

    else:
        page_state[slot_name][0]['cols'][0]['blocks'].append({
            'uid': IUUID(block)})

    page_configuration.store(page_state)


def migrate_sl_image_layout(old_object, new_object):
    block_layout_mapping = {
        'small': {
            'scale': 'sl_textblock_small',
            'imagefloat': 'left'},
        'middle': {
            'scale': 'sl_textblock_middle',
            'imagefloat': 'left'},
        'full': {
            'scale': 'sl_textblock_large',
            'imagefloat': 'no-float'},
        'middle-right': {
            'scale': 'sl_textblock_middle',
            'imagefloat': 'right'},
        'small-right': {
            'scale': 'sl_textblock_small',
            'imagefloat': 'right'},
        'no-image': {
            'scale': 'sl_textblock_small',
            'imagefloat': 'left'},
    }

    old_config = IBlockConfig(old_object)
    image_layout = old_config.get_image_layout()
    if not image_layout or image_layout == 'dummy-dummy-dummy':
        return

    new_config = IBlockConfiguration(new_object)
    cfg = new_config.load()
    cfg.update(block_layout_mapping[image_layout])
    new_config.store(cfg)


def migrate_simplelayout_page_state(old_page, new_page):
    for block in new_page.listFolderContents():
        if INewSLBlock.providedBy(block):
            raise ValueError('Block must be migrated after pages.')

        if not ISimpleLayoutBlock.providedBy(block):
            continue

        if ISlotBlock.providedBy(block) or IPortletColumn.providedBy(block):
            move_sl_block_into_slot(old_page, new_page, block, 'portletright')

        elif ISlotD.providedBy(block):
            move_sl_block_into_slot(old_page, new_page, block, 'bottom')

        else:
            move_sl_block_into_slot(old_page, new_page, block, 'default')


def migrate_lead_image_into_textblock(old_page, new_page):
    image = old_page.getImage()
    if not image or not image.get_size():
        # no lead image
        return

    assert IBlobWrapper.providedBy(image), \
        'Unexpectedly, the teaser image "{!r}" is not an IBlobWrapper.'.format(
            image)

    teaser_block = createContentInContainer(
        container=new_page,
        portal_type='ftw.simplelayout.TextBlock',
        title='Teaser'
    )

    fields = dict(reduce(list.__add__,
                         map(getFieldsInOrder, iterSchemata(teaser_block))))

    fields['show_title'].set(teaser_block, False)
    fields['image_alt_text'].set(
        teaser_block, old_page.getImageAltText().decode('utf-8'))
    fields['image_caption'].set(
        teaser_block, old_page.getImageCaption().decode('utf-8'))
    fields['open_image_in_overlay'].set(
        teaser_block, old_page.getImageClickable())

    new_image = fields['image']._type(
        data='',
        contentType=image.content_type,
        filename=image.filename.decode('utf-8'))
    new_image._blob = image.getBlob()
    fields['image'].set(teaser_block, new_image)

    # Since the teaser was stored on the *page*, the image layout of the
    # teaser is stored in the block-config of the page!
    # Therefore we must migrate the view from the page to the new
    # teaser block.
    migrate_sl_image_layout(old_page, teaser_block)
    move_sl_block_into_slot(old_page, new_page, teaser_block, 'default')


def migrate_image_to_file(obj):
    image = obj.getImage()

    # Use the functionality of the UpgradeStep
    class MigrateToFile(UpgradeStep):
        def __call__(self):
            # This is an AT => AT migration; we just replace the class.
            self.migrate_class(obj, File)

    MigrateToFile(obj.portal_setup)

    # clear archetypes.schemaextender cache
    getattr(obj.REQUEST, CACHE_KEY).pop(IUUID(obj), None)

    ifaces_to_remove = (set(providedBy(obj)) -
                        set(implementedBy(obj.__class__)))
    map(partial(noLongerProvides, obj), ifaces_to_remove)

    obj.Schema()
    obj.setFile(image)
    obj.setDocumentDate(obj.created())
    obj.portal_type = 'File'


class ContentPageMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(ContentPageMigrator, self).__init__(
            new_portal_type='ftw.simplelayout.ContentPage',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + LEAD_IMAGE_FIELDS
                + ('subject',)
                + ignore_fields),
            field_mapping=field_mapping,
            additional_steps=(
                (migrate_simplelayout_page_state,
                 migrate_lead_image_into_textblock)
                + additional_steps),
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'ContentPage'}
        if path:
            query['path'] = path
        return query


class NewsFolderMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(NewsFolderMigrator, self).__init__(
            new_portal_type='ftw.news.NewsFolder',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + ignore_fields
                + ('effectiveDate',
                   'expirationDate',
                   'subject')),
            field_mapping=field_mapping,
            additional_steps=(
                (self.create_news_listing_block, )
                + additional_steps),
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'NewsFolder'}
        if path:
            query['path'] = path
        return query

    def create_news_listing_block(self, old_news_folder, new_news_folder):
        from ftw.news.contents.news_folder import create_news_listing_block
        create_news_listing_block(new_news_folder)


class NewsMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(NewsMigrator, self).__init__(
            new_portal_type='ftw.news.News',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + LEAD_IMAGE_FIELDS
                + ignore_fields
                + (
                    'content_categories',  # no longer exists
                    'excludeFromNav',  # all news are excluded by default
                    'topics',  # no topics for news
                )),
            field_mapping=field_mapping,
            additional_steps=(
                (migrate_simplelayout_page_state,
                 migrate_lead_image_into_textblock)
                + additional_steps),
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'News'}
        if path:
            query['path'] = path
        return query


class EventFolderMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(EventFolderMigrator, self).__init__(
            new_portal_type='ftw.events.EventFolder',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + ignore_fields
                + ('effectiveDate',
                   'expirationDate',
                   'subject')),
            field_mapping=field_mapping,
            additional_steps=(
                (self.create_event_listing_block, )
                + additional_steps),
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'EventFolder'}
        if path:
            query['path'] = path
        return query

    def create_event_listing_block(self, old_event_folder, new_event_folder):
        from ftw.events.contents.eventfolder import create_event_listing_block
        create_event_listing_block(new_event_folder)


class EventPageMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        field_mapping = field_mapping or {}
        field_mapping.update({
            'endDate': 'end',
            'startDate': 'start',
            'wholeDay': 'whole_day'})

        super(EventPageMigrator, self).__init__(
            new_portal_type='ftw.events.EventPage',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + LEAD_IMAGE_FIELDS
                + (
                    'content_categories',  # no longer exists
                    'excludeFromNav',  # all events are excluded by default
                    'topics',  # no topics for events
                )
                + ignore_fields),
            field_mapping=field_mapping,
            additional_steps=(
                (self.ensure_timezone,
                 migrate_simplelayout_page_state,
                 migrate_lead_image_into_textblock)
                + additional_steps),
            options=options,
        )

    def ensure_timezone(self, old_object, new_object):
        # The "timezone" field was removed in newer p.a.event versions.
        if IEventBasic(new_object).timezone:
            return

        # We do not use the behavior on purpose here in order to
        # bypass the timezone setter.
        new_object.timezone = u'Europe/Zurich'

    def query(self, path=None):
        query = {'portal_type': 'EventPage'}
        if path:
            query['path'] = path
        return query

class ImageToSliderPaneMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        super(ImageToSliderPaneMigrator, self).__init__(
            new_portal_type='ftw.slider.Pane',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + SL_BLOCK_DEFAULT_IGNORED_FIELDS
                + ignore_fields
                + (
                    'description',  # was invisible
                )),
            field_mapping=field_mapping,
            additional_steps=additional_steps,
            options=options,
        )

    def migrate_object(self, old_object):
        if old_object.portal_type not in ('Image',):
            raise ValueError(
                'Unsupported source portal_type {!r}'
                .format(old_object.portal_type))
        return super(ImageToSliderPaneMigrator, self).migrate_object(old_object)


class TextBlockMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        field_mapping = field_mapping or {}
        field_mapping.update({
            'showTitle': 'show_title',
            'imageAltText': 'image_alt_text',
            'imageCaption': 'image_caption',
            'imageClickable': 'open_image_in_overlay',
            'teaserExternalUrl': 'external_link',
            'teaserReference': 'internal_link'})

        super(TextBlockMigrator, self).__init__(
            new_portal_type='ftw.simplelayout.TextBlock',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + SL_BLOCK_DEFAULT_IGNORED_FIELDS
                + ignore_fields
                + (
                    'description',  # was invisible
                    'teaserSelectLink',  # selection is now automatic => drop
                )),
            field_mapping=field_mapping,
            additional_steps=(migrate_sl_image_layout,) + additional_steps,
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'TextBlock'}
        if path:
            query['path'] = path
        return query


class AddressBlockMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        field_mapping = field_mapping or {}
        field_mapping.update({
            'addressTitle': 'address_title',
            'extraAddressLine': 'extra_address_line',
            'extraAddressLine': 'extra_address_line',
            'openingHours': 'opening_hours',
            'openingHours': 'opening_hours',
            'zip': 'zip_code'})

        super(AddressBlockMigrator, self).__init__(
            new_portal_type='ftw.addressblock.AddressBlock',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + SL_BLOCK_DEFAULT_IGNORED_FIELDS
                + ignore_fields
                + (
                    'description',
                    'showOpeningHours',
                    'showTitle',
                )),
            field_mapping=field_mapping,
            additional_steps=additional_steps,
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'AddressBlock'}
        if path:
            query['path'] = path
        return query


class HTMLBlockMigrator(InplaceMigrator):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        field_mapping = field_mapping or {}
        field_mapping.update({
            'showTitle': 'show_title',
            'text': 'content'})

        super(HTMLBlockMigrator, self).__init__(
            new_portal_type='ftw.htmlblock.HtmlBlock',
            ignore_fields=(
                DUBLIN_CORE_IGNORES
                + SL_BLOCK_DEFAULT_IGNORED_FIELDS
                + ignore_fields
                + (
                    'description',  # was invisible
                )),
            field_mapping=field_mapping,
            additional_steps=additional_steps,
            options=options,
        )

    def query(self, path=None):
        query = {'portal_type': 'HTMLBlock'}
        if path:
            query['path'] = path
        return query


class ListingBlockMigrator(object):

    def __init__(self, ignore_fields=(), additional_steps=(), options=0,
                 field_mapping=None):
        if IMPORT_ERROR:
            raise IMPORT_ERROR

        # Old listing blocks may be migrated to new listing blocks or may
        # become gallery blocks when suitable.
        # https://github.com/4teamwork/izug.organisation/issues/890

        ignore_fields = DUBLIN_CORE_IGNORES + SL_BLOCK_DEFAULT_IGNORED_FIELDS + (
            'description',  # hidden thus unused
        ) + ignore_fields

        field_mapping = field_mapping or {}
        field_mapping.update({
            'showTitle': 'show_title',
            'sortOn': 'sort_on',
            'sortOrder': 'sort_order',
            'tableColumns': 'columns'})

        self.filelisting_migrator = InplaceMigrator(
            new_portal_type='ftw.simplelayout.FileListingBlock',
            ignore_fields=ignore_fields + ('slick_settings',),
            field_mapping=field_mapping,
            additional_steps=additional_steps,
            options=options,
        )

        self.gallery_migrator = InplaceMigrator(
            new_portal_type='ftw.simplelayout.GalleryBlock',
            ignore_fields=ignore_fields + (
                'slick_settings',
                'sortOn',
                'sortOrder',
                'tableColumns'),
            field_mapping=field_mapping,
            additional_steps=additional_steps,
            options=options,
        )

        self.sliderblock_migrator = InplaceMigrator(
            new_portal_type='ftw.sliderblock.SliderBlock',
            ignore_fields=ignore_fields + (
                'sortOn',
                'sortOrder',
                'tableColumns'),
            field_mapping={
                'showTitle': 'show_title',
                'slick_settings': 'slick_config'},
            additional_steps=additional_steps,
            options=options,
        )

        self.image_to_slider_pane_migrator = ImageToSliderPaneMigrator(
            ignore_fields=ignore_fields,
            field_mapping=field_mapping,
            options=options)

    def query(self, path=None):
        query = {'portal_type': 'ListingBlock'}
        if path:
            query['path'] = path
        return query

    def migrate_object(self, old_object):
        view = IBlockConfig(old_object).get_viewname()
        if view not in (None, '', 'gallery', 'dummy', 'block_view', 'slider'):
            raise ValueError('ListingBlock: unexpected view {!r}'.format(view))

        children_types = set(map(attrgetter('portal_type'),
                                 old_object.objectValues()))

        if view == 'slider' and children_types == {'Image'}:
            map(self.image_to_slider_pane_migrator.migrate_object,
                old_object.objectValues()[:])
            self.sliderblock_migrator.migrate_object(old_object)

        elif not children_types or children_types == {'File'}:
            self.filelisting_migrator.migrate_object(old_object)

        elif children_types == {'Image'}:
            self.gallery_migrator.migrate_object(old_object)

        elif children_types == {'File', 'Image'}:
            # convert all "Image" children to "File"
            map(migrate_image_to_file,
                filter(lambda child: child.portal_type=='Image',
                       old_object.objectValues()))

            self.filelisting_migrator.migrate_object(old_object)

        else:
            raise ValueError('ListingBlock: unexpected children: {}'.format(
                children_types))
