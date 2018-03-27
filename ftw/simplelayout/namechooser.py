from Acquisition import aq_inner
from OFS.ObjectManager import bad_id
from plone import api
from plone.app.content.namechooser import ATTEMPTS
from plone.app.content.namechooser import NormalizingNameChooser as PloneNormalizingNameChooser
from plone.i18n.normalizer import FILENAME_REGEX
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
import time


class NormalizingNameChooser(PloneNormalizingNameChooser):

    def _findUniqueName(self, name, object):
        """
        Copied from the parent class and enhanced with a check for the invalid
        ids stored in the site properties.
        """
        check_id = self._getCheckId(object)

        if not check_id(name, required=1) and not self.check_invalid_ids(name):
            return name

        ext = ''
        m = FILENAME_REGEX.match(name)
        if m is not None:
            name = m.groups()[0]
            ext = '.' + m.groups()[1]

        idx = 1
        while idx <= ATTEMPTS:
            new_name = "%s-%d%s" % (name, idx, ext)
            if not check_id(new_name, required=1) and not self.check_invalid_ids(new_name):
                return new_name
            idx += 1

        # give one last attempt using the current date time before giving up
        new_name = "%s-%s%s" % (name, time.time(), ext)
        if not check_id(new_name, required=1) and not self.check_invalid_ids(new_name):
            return new_name

        raise ValueError(
            "Cannot find a unique name based on %s after %d attemps." % (
                name,
                ATTEMPTS,
            )
        )

    def _getCheckId(self, object):
        """
        Copied from the parent class.
        """
        parent = aq_inner(self.context)

        # Customization: get the script from the parent instead of the given object.
        _check_id = getattr(parent, 'check_id', None)

        if _check_id is not None:
            def do_Plone_check(id, required):
                return _check_id(id, required=required, contained_by=parent)
            check_id = lambda id, required: do_Plone_check(id, required)
        else:
            def do_OFS_check(parent, id):
                try:
                    parent._checkId(id)
                except BadRequest:
                    return True
            check_id = lambda id, required: do_OFS_check(parent, id)
        return check_id

    def check_invalid_ids(self, id):
        """
        Inspired by `Products.CMFFormController.FormController.FormController#_checkId`.
        """
        portal = api.portal.get()
        if not id:
            return 'Empty id'
        s = bad_id(id)
        if s:
            return '%s is not a valid id' % (id)
        # extra checks for Plone sites
        if portal.__class__.__name__ == 'PloneSite':
            props = getToolByName(portal, 'portal_properties', None)
            if props is not None:
                if hasattr(props, 'site_properties') and \
                   hasattr(props.site_properties, 'invalid_ids'):
                    if id in props.site_properties.invalid_ids:
                        return '%s is a reserved id' % (id)
