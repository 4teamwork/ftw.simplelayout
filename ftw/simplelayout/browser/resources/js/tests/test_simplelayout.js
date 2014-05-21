var assert = chai.assert;


suite('Test simplelayout configuration', function() {

    setup(function() {
        $structure = $(
            '<div class="simplelayout">' +
            '<div class="sl-block"></div>' +
            '</div>');

        $structure.appendTo('body');

    });

    test('Simplelayout defaults if no options nor data config is present', function() {
        $('.simplelayout').simplelayout('init');

        var data = $('.simplelayout').data('simplelayout');
        assert.isObject(data, 'No simplelayout data object found');

        assert.strictEqual('.sl-block', data.blocks);
        assert.strictEqual('#content', data.contentarea);
        assert.strictEqual(2, data.columns);
        assert.strictEqual(2, data.images);
        assert.strictEqual(10, data.margin_right);
        assert.strictEqual(960, data.contentwidth);
        assert.strictEqual(false, data.editable);
    });

    test('Override default with options', function() {
        $('.simplelayout').simplelayout('init', {
            columns: 4,
            contentwidth: 640
        });

        var data = $('.simplelayout').data('simplelayout');
        assert.strictEqual(4, data.columns);
        assert.strictEqual(640, data.contentwidth);
    });


    test('Load simplelayout defaults with simplelayout-config data object', function() {
        var $simplelayout = $('.simplelayout');
        $simplelayout.data('simplelayout-config', {
            columns: 4,
            contentwidth: 640
        });
        $('.simplelayout').simplelayout('init');

        var data = $('.simplelayout').data('simplelayout');
        assert.strictEqual(4, data.columns);
        assert.strictEqual(640, data.contentwidth);
    });


    teardown(function() {

        $('.simplelayout').remove();
    });


});