from ftw.simplelayout import config
from Products.Archetypes import atapi
from Products.CMFCore import utils
from zope.i18nmessageid import MessageFactory


_ = MessageFactory('ftw.simplelayout')


def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Regstrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """

    import ftw.simplelayout.contents.file
    import ftw.simplelayout.contents.image
    import ftw.simplelayout.contents.link
    import ftw.simplelayout.contents.page
    import ftw.simplelayout.contents.paragraph
    ftw  # pylint: disable=W0104

    content_types, constructors, _ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
                          content_types=(atype,),
                          permission=config.ADD_PERMISSIONS[atype.portal_type],
                          extra_constructors=(constructor,),
                          ).initialize(context)
