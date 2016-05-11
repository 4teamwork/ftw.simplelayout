from zope.interface import Interface


class IOpenGraphSupport(Interface):
    """Marker Interface for Opengraphable content"""


class IOpenGraphDataProvider(Interface):
    """Data provider for opengraphable content
        By default it needs to provide the basic metadata fields:
        - og:title
        - og:type
        - og:image
        - og:url

        I a content is part of larger website you can also provide:
        - og:site:name

        You can provide more fields as you wish, check http://ogp.me

        We use a OrderedDict, since the OG is ordered.
    """

    def __init__(context, request, view):
        """adapts context and request and view"""

    def get_title():
        """OG Title"""

    def get_type():
        """OG type"""

    def get_url():
        """OG url"""

    def get_image_url():
        """OG image"""

    def get_site_name():
        """OG site name"""

    def collect_og_data():
        """Returns a ordered dict with all og:key, value"""
