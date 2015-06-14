from zope.i18nmessageid import MessageFactory


_ = MessageFactory('ftw.simplelayout')


def initialize(context):

    from ftw.simplelayout.browser.provider import SimplelayoutExpression
    from Products.Five.browser.pagetemplatefile import getEngine
    from zope.tales.tales import RegistrationError

    zope_engine = getEngine()

    try:
        zope_engine.registerType('simplelayout', SimplelayoutExpression)
    except RegistrationError:
        # zope.reload support
        pass

    try:
        from five.pt import engine
        from ftw.simplelayout.browser.provider import (
            ChameleonSimplelayoutExpression
        )
    except ImportError:
        pass
    else:
        engine.Program.expression_types[
            'simplelayout'] = ChameleonSimplelayoutExpression
