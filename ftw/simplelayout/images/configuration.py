from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from plone import api


class Configuration(object):
    """The image-related configuration requires a special format to be customizable.
    """
    def image_limits(self):
        # Example limit-configuration line:
        # 'ftw.simplelayout.TextBlock => soft:width=123,height=222;hard:width=123'

        limits = {}
        entries = self._get_registry_property('image_limits')

        for entry in entries:
            entry = entry.encode('utf-8')

            # 'ftw.simplelayout.TextBlock', 'soft:width=123,height=222;hard:width=123'
            portal_type, value = map(str.strip, entry.split('=>'))
            if portal_type not in limits:
                limits[portal_type] = {}

            # ['soft:width=123 ,height=222', 'hard:width=123']
            for limit_type_configuration in map(str.strip, value.split(';')):

                # 'soft', 'width=123 ,height=222'
                limit_type, dimensions = map(str.strip, limit_type_configuration.split(':'))

                if limit_type not in limits[portal_type]:
                    limits[portal_type][limit_type] = {}

                # ['width=123', 'height=222']
                for dimension in map(str.strip, dimensions.split(',')):

                    # 'width', 123
                    dimension_name, value = map(str.strip, dimension.split('='))

                    if dimension_name not in limits[portal_type][limit_type]:
                        limits[portal_type][limit_type][dimension_name] = {}

                    limits[portal_type][limit_type][dimension_name] = int(value)

        # Output example
        # {'ftw.simplelayout.TextBlock':
        #     {'hard': {'width': '150'},
        #      'soft': {'height': '300', 'width': '400'}},
        #  'ftw.slider.Pane': {
        #      'hard': {'width': '150'},
        #      'soft': {'height': '300', 'width': '900'}}}
        return limits

    def aspect_ratios(self):
        # Example aspect_ration-configuration line:
        # 'ftw.simplelayout.TextBlock => 4/3::1.33333;16/9::1.7777'
        entries = self._get_registry_property('image_cropping_aspect_ratios')
        aspect_ratios = {}

        for entry in entries:
            entry = entry.encode('utf-8')

            # 'ftw.simplelayout.TextBlock', '4/3::1.33333;16/9::1.7777'
            portal_type, value = map(str.strip, entry.split('=>'))
            if portal_type not in aspect_ratios:
                aspect_ratios[portal_type] = []

            # ['4/3::1.33333, '16/9::1.7777']
            for aspect_ration_configuration in map(str.strip, value.split(';')):

                # '4/3', '1.33333'
                title, ratio = map(str.strip, aspect_ration_configuration.split('::'))
                aspect_ratios[portal_type].append({
                    'title': title,
                    'value': ratio
                    })

        # Output example
        # {'ftw.simplelayout.TextBlock':
        #     [
        #         {"title": '4/3', "value": 1.33333},
        #         {"title": '16/9', "value": 1.77778}
        #     ]
        # }
        return aspect_ratios

    def _get_registry_property(self, name):
        return api.portal.get_registry_record(
            name=name, interface=ISimplelayoutDefaultSettings)
