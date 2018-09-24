from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from plone import api


class Configuration(object):
    """The image-related configuration requires a special format to be customizable.
    """
    def image_limits(self):
        # Example limit-configuration line:
        # {'ftw.simplelayout.TextBlock': [
        #     soft:width=123, height=222,
        #     hard:width=123]
        # }

        limits = {}
        entries = self._get_registry_property('image_limits')

        for portal_type, values in entries.items():
            limits[portal_type] = {}

            # [soft:width=123,height=222, hard:width=123]
            for value in values:
                value = value.encode('utf-8')

                # 'soft', ['width=123 ,height=222']
                limit_type, dimensions = map(str.strip, value.split(':'))
                limits[portal_type][limit_type] = {}

                # ['width=123', 'height=222']
                for dimension in map(str.strip, dimensions.split(',')):

                    # 'width', 123
                    dimension_name, value = map(str.strip, dimension.split('='))
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
        # {'ftw.simplelayout.TextBlock': ['4/3 => 1.33333', '16/9 => 0.7777']
        entries = self._get_registry_property('image_cropping_aspect_ratios')
        aspect_ratios = {}

        for portal_type, values in entries.items():
            aspect_ratios[portal_type] = []

            # ['4/3 => 1.33333', '16/9 => 0.7777']
            for value in values:
                value = value.encode('utf-8')

                # '4/3', '1.33333'
                title, ratio = map(str.strip, value.split('=>'))
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
