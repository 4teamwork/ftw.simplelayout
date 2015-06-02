from zope.i18nmessageid import MessageFactory


_ = MessageFactory('ftw.simplelayout')


def initialize(context):

    from ftw.simplelayout.browser.provider import TalesSimplelayoutExpression
    from Products.Five.browser.pagetemplatefile import getEngine
    from zope.tales.tales import RegistrationError

    zope_engine = getEngine()
    try:
        zope_engine.registerType('simplelayout', TalesSimplelayoutExpression)
    except RegistrationError:
        # zope.reload support
        pass
