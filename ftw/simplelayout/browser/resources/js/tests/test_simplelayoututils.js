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


suite('Resize block will also resize the containing image', function(){
    // Note: The calculation also includes the grid margin

    setup(function(){
        settings = {
            contentwidth: 960,
            contentarea: '#content',
            margin_right: 10,
            columns: 4,
            images: 2};
    });


    test('The image can not be smaller than one image column', function(){
        new_width = $.fn.simplelayoututils.get_image_width_based_on_block_width;

        // Resize block from 480px to 240px - image width is too small
        assert.strictEqual(
            110,
            new_width(
                image_width=50,
                origin_block_width=480,
                new_block_width=240,
                settings=settings
                ));

    });

    test('The image width automatially aligns to grid', function(){
        new_width = $.fn.simplelayoututils.get_image_width_based_on_block_width;

        //Resize block from 480px to 240px - image width does not fit the grid.
        assert.strictEqual(
            110,
            new_width(
                image_width=167,
                origin_block_width=480,
                new_block_width=240,
                settings=settings
                ));

    });


    test('If the block size is devided in half, also the image should be halved', function(){
        new_width = $.fn.simplelayoututils.get_image_width_based_on_block_width;

        //Resize block from 480px to 240px
        assert.strictEqual(
            110,
            new_width(
                image_width=230,
                origin_block_width=480,
                new_block_width=240,
                settings=settings
                ));

        //Resize block from 960px to 480px
        assert.strictEqual(
            230,
            new_width(
                image_width=470,
                origin_block_width=960,
                new_block_width=480,
                settings=settings
                ));


    });

    test('If the image machtes the block size, always match the block size', function(){
        new_width = $.fn.simplelayoututils.get_image_width_based_on_block_width;

        //Resize block from 480px to 240px
        assert.strictEqual(
            230,
            new_width(
                image_width=470,
                origin_block_width=480,
                new_block_width=240,
                settings=settings
                ));

        //Resize block from 960px to 480px
        assert.strictEqual(
            470,
            new_width(
                image_width=950,
                origin_block_width=960,
                new_block_width=480,
                settings=settings
                ));

        //Resize block from 240x to 960px
        assert.strictEqual(
            950,
            new_width(
                image_width=230,
                origin_block_width=240,
                new_block_width=960,
                settings=settings
                ));

        //Resize block from 960 to 720px
        assert.strictEqual(
            710,
            new_width(
                image_width=950,
                origin_block_width=960,
                new_block_width=720,
                settings=settings
                ));

        //Resize block from 720 to 240px
        assert.strictEqual(
            230,
            new_width(
                image_width=710,
                origin_block_width=720,
                new_block_width=240,
                settings=settings
                ));
    });


    test('The image can never be bigger than the block', function(){
        new_width = $.fn.simplelayoututils.get_image_width_based_on_block_width;

        // Resize block from 480px to 960px
        assert.strictEqual(
            950,
            new_width(
                image_width=1000,
                origin_block_width=480,
                new_block_width=960,
                settings=settings
                ));

        // Resize block from 480px to 240px
        assert.strictEqual(
            230,
            new_width(
                image_width=488,
                origin_block_width=480,
                new_block_width=240,
                settings=settings
                ));

    });

});


suite('Test reload a block', function(){

    setup(function() {
        this.clock = sinon.useFakeTimers();
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;

        this.server.respondWith("POST", "./@@sl-ajax-reload-block-view",
            [200, {'Content-Type': 'text/html'}, '' +
            '<h2>Block title</h2>' +
            '<div>Dummy content</div>'
          ]);

        $controls.appendTo('#content');
        $structure.appendTo('#content');
    });

    test('Test if sl-block-reload can be triggerd on block view wrapper.', function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        $('.sl-block .block-view-wrapper').trigger('sl-block-reload');
        this.clock.tick(100);
        assert.strictEqual('Block title', $('.sl-block .block-view-wrapper h2').html());
        assert.strictEqual('Dummy content', $('.sl-block .block-view-wrapper div').html());

    });

    teardown(function() {
        this.clock.restore();
        this.server.restore();
        $('.simplelayout-page-controls').remove();
        $('.simplelayout').remove();
    });

});
