var assert = chai.assert;


suite('Test simplelayout configuration', function() {

    setup(function() {

        $controls = $(
            '<fieldset class="simplelayout-page-controls">' +
            '<legend>Controls</legend>' +
            '<a href="#" id="add-block-link">Add Block</a>' +
            '<input type="checkbox" id="auto-block-height" name="auto-block-height" />' +
            '<label for="auto-block-height">Enable auto block height</label>' +
            '<a href="./simplelayout_info" id="simplelayout-info-link">Info</a>' +
            '<a href="" id="simplelayout-help-link" target="_blank">Help</a>' +
            '</fieldset>');

        $structure = $(
            '<div class="simplelayout">' +
            '<div class="sl-block"></div>' +
            '</div>');

        $structure.appendTo('#content');

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

    test('Override defaults with options', function() {
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


suite('Test simplelayout page controls', function(){

    setup(function() {
        this.server = sinon.fakeServer.create();
        this.server.autoRespond = true;
        this.server.respondWith(/@@addable-blocks-view /, function (xhr, id) {
          xhr.respond(200, { 'Content-Type': 'text/html' }, '' +
            '<html><body>' +
            '<div id="content">Fake content</div>' +
            '</body></html>'
          );
        });

        $controls = $(
            '<fieldset class="simplelayout-page-controls">' +
            '<legend>Controls</legend>' +
            '<a href="#" id="add-block-link">Add Block</a>' +
            '<input type="checkbox" id="auto-block-height" name="auto-block-height" />' +
            '<label for="auto-block-height">Enable auto block height</label>' +
            '<a href="./simplelayout_info" id="simplelayout-info-link">Info</a>' +
            '<a href="" id="simplelayout-help-link" target="_blank">Help</a>' +
            '</fieldset>');

        $structure = $(
            '<div class="simplelayout">' +
            '<div class="sl-block"></div>' +
            '</div>');

        $controls.appendTo('#content');
        $structure.appendTo('#content');

    });

    test('ContentPage controls are turned into jquery ui buttons', function(){
        $('.simplelayout').simplelayout('init', {'editable': true});

        assert.isTrue($('#add-block-link', $controls).hasClass('ui-button'));
        assert.isTrue($('#simplelayout-info-link', $controls).hasClass('ui-button'));
        assert.isTrue($('#simplelayout-help-link', $controls).hasClass('ui-button'));
        assert.isTrue($('#auto-block-height', $controls).hasClass('ui-helper-hidden-accessible'));
    });

    test("Click on 'add new block' button", function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        $('#add-block-link').click();
        assert.isObject($('.sl-add-block.sl-block'));

    });


    teardown(function() {
        this.server.restore();
        $controls.remove();
        $structure.remove();
    });


});