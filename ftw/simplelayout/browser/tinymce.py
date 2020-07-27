from Products.CMFPlone.interfaces import IPatternsSettings
from Products.CMFPlone.patterns.settings import PatternSettingsAdapter
from zope.interface import implementer
import json


@implementer(IPatternsSettings)
class SimplelayoutPatternSettingsAdapter(PatternSettingsAdapter):
    def tinymce(self):
        config = super(SimplelayoutPatternSettingsAdapter, self).tinymce()
        data_config = json.loads(config['data-pat-tinymce'])

        # Original 'prependToUrl': '{0}/resolveuid/'.format(site_path.rstrip('/')),
        data_config['prependToUrl'] = 'resolveuid/'
        return {'data-pat-tinymce': json.dumps(data_config)}
