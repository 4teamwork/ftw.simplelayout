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

    test('is_image (Return true if it is an image))', function(){
        var file = {'type': 'image/png'};
        assert.isTrue($.fn.simplelayoututils.is_image(file));

        file.type = 'image/gif';
        assert.isTrue($.fn.simplelayoututils.is_image(file));

        file.type = 'image/jpg';
        assert.isTrue($.fn.simplelayoututils.is_image(file));

        file.type = 'image/jpeg';
        assert.isTrue($.fn.simplelayoututils.is_image(file));
    });

    test('is_image (Return false if it is NOT an image))', function(){
        var file = {'type': 'application/pdf'};
        assert.isFalse($.fn.simplelayoututils.is_image(file));
    });


    teardown(function() {
        // Restore origin font-size
        $('#content').css('font-size', saved_font_size);
    });

});