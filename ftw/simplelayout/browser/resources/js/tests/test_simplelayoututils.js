var assert = chai.assert;

suite('Test simplelayout utils', function() {

    setup(function(){
        settings = {
            contentwidth: 960,
            contentarea: '#content',
            columns: 4,
            images: 2};

        saved_font_size = $('#content').css('font-size');
    });

    test('get_grid (divides contentwidth with amount of columns)', function(){
        assert.strictEqual(240, $.fn.simplelayoututils.get_grid(settings));

        settings.contentwidth = 100;
        assert.strictEqual(25, $.fn.simplelayoututils.get_grid(settings));
    });

    test('get_image_grid (divides contentwidth with amount of columns and amount of images)', function(){
        assert.strictEqual(120, $.fn.simplelayoututils.get_image_grid(settings));

        settings.contentwidth = 200;
        assert.strictEqual(25, $.fn.simplelayoututils.get_image_grid(settings));
    });

    test('get_grid_height (gets the font size of the content container, as number)', function(){
        $('#content').css('font-size', '12px');
        assert.strictEqual(12, $.fn.simplelayoututils.get_grid_height(settings));

        $('#content').css('font-size', '10');
        assert.strictEqual(10, $.fn.simplelayoututils.get_grid_height(settings));
    });


    teardown(function() {
        // Restore origin font-size
        $('#content').css('font-size', saved_font_size);
    });

});