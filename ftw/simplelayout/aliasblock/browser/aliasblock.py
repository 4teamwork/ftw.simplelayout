from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from ftw.simplelayout.browser.blocks.base import BaseBlock


class AliasBlockView(BaseBlock):

    template = ViewPageTemplateFile('templates/aliasblock.pt')
