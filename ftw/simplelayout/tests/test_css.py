from ftw.simplelayout.testing import FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING
from ftw.simplelayout.testing import SimplelayoutTestCase
from ftw.theming.interfaces import ISCSSCompiler
from path import Path
from zope.component import getMultiAdapter


class TestCSSIsUpToDate(SimplelayoutTestCase):

    layer = FTW_SIMPLELAYOUT_FUNCTIONAL_TESTING

    def setUp(self):
        super(TestCSSIsUpToDate, self).setUp()
        self.compiler = getMultiAdapter(
            (self.layer['portal'], self.layer['request']),
            ISCSSCompiler)

    def test_css_is_up_to_date(self):
        cssfile = Path(__file__).joinpath(
            '..', '..', 'browser', 'resources', 'icons.css').abspath()

        files = list(self.get_source_files_by_path(
            'ftw/theming/resources/scss/globals/variables.scss',
            'ftw/simplelayout/browser/resources/theming.toolbar-icons.scss',
        ))

        result = self.compiler._compile(files)

        # SET THIS TO TRUE TEMPORARILY TO UPDATE icons.css
        if False:  # This should be False when committing!
            cssfile.write_text(result)

        # Yes, I dont want the CSS to be printed in the assertion
        # message, thus I use self.assertTrue.
        self.assertTrue(cssfile.bytes() == result,
                        'The icons.css is not up to date.'
                        ' Read this test to update the icons.css file.')

    def get_source_files_by_path(self, *paths):
        for sourcefile in self.compiler._get_scss_files():
            for path in paths:
                if str(sourcefile.origin).endswith(path):
                    yield sourcefile
