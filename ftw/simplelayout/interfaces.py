# pylint: disable=E0211, E0213
# E0211: Method has no argument
# E0213: Method should have "self" as first argument

from ftw.simplelayout import _
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope import schema
from zope.interface import Interface
from zope.interface import provider


class ISimplelayoutLayer(Interface):
    """Browserlayer for simplelayout"""


class ISimplelayout(Interface):
    """Marker for Simplelayout content pages"""


class ISimplelayoutBlock(Interface):
    """Marker for simplelayout blocks"""


@provider(IFormFieldProvider)
class IContentPageShowTitle(model.Schema):
    """Adds checkbox to hide title of a contentpage"""

    show_title = schema.Bool(
        title=_(u'Show title'),
        default=True,
        required=False
    )

    directives.write_permission(
        show_title='ftw.simplelayout.HideTitle')


class ISimplelayoutView(Interface):
    """@@simplelayout-view view interface.
    """


class ISimplelayoutBlockView(Interface):
    """Marker interface for simplelayout block views.
    """


class IPageConfiguration(Interface):
    """Adapter for storing simplelayout page configuration.
    """

    def store(json_conf):
        """Store the given configuration.
        """

    def load():
        """Load current configuration.
        """


class IBlockConfiguration(Interface):
    """Adapter for storing block configuration.
    """

    def store(json_conf):
        """Store the given configuration.
        """

    def load():
        """Load current configuration.
        """


class IBlockProperties(Interface):
    """Adapter for getting and setting information such as the current
    selected view for the block or the available views.
    """

    def __init__(context, request):
        """Adapts context and request.
        """

    def get_current_view_name():
        """Returns the name of the simplelayout view for displaying the
        context.
        """

    def set_view(name):
        """Sets the current view of the context to ``name``.
        """


class ISimplelayoutDefaultSettings(Interface):
    """Stores simplelayout default settings for the hole site"""

    slconfig = schema.Text(
        title=_(u'Simplelayout default configuration'),
        description=(_(
            u'desc_sl_config_control_panel',
            default=u'Add Simplelayout default'
            u'configuration, Check simplelayout'
            u'docu: https://github.com/4teamwork/ftw.simplelayout#usage')),
        default=u'{}',
        required=False)

    opengraph_plone_root = schema.Bool(
        title=_(u'Enable OpenGraph support on plone root'),
        default=True,
        required=False
    )

    opengraph_global_type = schema.TextLine(
        title=_(u'OpenGraph global type'),
        description=_(u'Check possible values on http://ogp.me'),
        default=u'website',
        required=False
    )


class IBlockModifier(Interface):
    """Block specific modifier"""

    def __init__(context, request):
        """Adapts context and request"""

    def modify(data):
        """Modifications based on data in the request"""


class ISimplelayoutActions(Interface):
    """Serves the simplelayout actions"""

    def __init__(context, request):
        """Adapts context and request.
        """

    def default_actions():
        """Default actions"""

    def specific_actions():
        """Specific actions"""


class ISimplelayoutContainerConfig(Interface):
    """Modify simplelayout settings adapter"""

    def __init__(context, request):
        """Adapts context and request.
        """

    def __call__(settings):
        """Receives a settings dict for modification - no return value."""

    def default_page_layout():
        """Define a set of default layouts. A new simplelayout page
        automatically renders the defined layouts.

        Example:
            return {
                "default": [
                    {"cols": [{"blocks": []}]}
                ]
            }

        Results in one layout with one.
        Return None, will trigger a fallback to on layout with one column.
        """
