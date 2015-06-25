from ftw.simplelayout.contents.interfaces import IListingBlockColumns
from ftw.table.interfaces import ITableGenerator
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import queryMultiAdapter
from zope.component import queryUtility


class GalleryBlockView(BrowserView):
    """GalleryBlock default view"""
