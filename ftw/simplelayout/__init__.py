import pkg_resources
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('ftw.simplelayout')


try:
    if pkg_resources.get_distribution('ftw.sliderblock').version < '2.0':
        try:
            pkg_resources.require('collective.quickupload')
        except pkg_resources.DistributionNotFound:
            msg = ("ftw.sliderblock < 2.0 requires collective.quickupload which is"
                   " not installed. Either upgrade ftw.sliderblock >= 2.0 "
                   "(recommended) or install collective.upload.")
            raise ImportError(msg)
except pkg_resources.DistributionNotFound:
    pass


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
