from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer


def normalize_portal_type(portal_type):
    normalizer = getUtility(IIDNormalizer)
    return normalizer.normalize(portal_type)
