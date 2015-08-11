from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.Transform import make_config_persistent


def default_profile_installed(site):
    add_iframe_to_allowed_tags(site)


def add_iframe_to_allowed_tags(context):
    safe_html = getToolByName(context, 'portal_transforms')['safe_html']
    config = safe_html._config
    valid_tags = config['valid_tags']

    if 'iframe' not in valid_tags:
        valid_tags['iframe'] = 1

        make_config_persistent(config)
        safe_html._p_changed = True
        safe_html.reload()
