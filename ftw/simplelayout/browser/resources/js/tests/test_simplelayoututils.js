var assert = chai.assert;

suite('Test simplelayout utils', function() {

    setup(function(){
        settings = {contentwidth: 960, columns: 4};
    });

    test('get_grid (divides contentwidth with amount of columns)', function(){
        assert.strictEqual(240, $.fn.simplelayoututils.get_grid(settings));

        settings.contentwidth = 100;
        assert.strictEqual(25, $.fn.simplelayoututils.get_grid(settings));
    });

});