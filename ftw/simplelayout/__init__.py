"""Main product initializer
"""

from zope.i18nmessageid import MessageFactory


simplelayoutkMessageFactory = MessageFactory('ftw.simplelayout')


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
