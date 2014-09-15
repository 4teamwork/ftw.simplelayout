var assert = chai.assert;
var $controls = $(
    '<fieldset class="simplelayout-page-controls">' +
    '<legend>Controls</legend>' +
    '<a href="#" id="add-block-link">Add Block</a>' +
    '<input type="checkbox" id="auto-block-height" name="auto-block-height" />' +
    '<label for="auto-block-height">Enable auto block height</label>' +
    '<a href="./simplelayout_info" id="simplelayout-info-link">Info</a>' +
    '<a href="" id="simplelayout-help-link" target="_blank">Help</a>' +
    '</fieldset>');

var $structure = $(
    '<div class="simplelayout">' +
    '<div class="sl-block" data-uuid="FAKEUID">' +
    '<div class="block-view-wrapper">' +
    '<div class="sl-img-wrapper">' +
    '<img src="../assets/example.jpg" />' +
    '</div>' +
    '</div>' +
    '</div>' +
    '</div>');



suite('Test simplelayout configuration', function() {

    setup(function() {

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
        $('.simplelayout-page-controls').remove();
        $('.simplelayout').remove();
    });


});

suite('Test simplelayout public "layout" method', function(){

    setup(function() {
        $controls.appendTo('#content');
        $structure.appendTo('#content');

    });

    test("Margin-right on every block", function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        assert.strictEqual('10px', $('.block-view-wrapper').eq(0).css('margin-right'));

    });

    test("Max-width is set on simplelayout div", function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        assert.strictEqual('960px', $('.simplelayout').css('max-width'));

    });


    test("Width is set on simplelayout div in edit mode (prevent responsive behavior)", function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        assert.strictEqual('960px', $('.simplelayout').css('width'));

    });


    test("Expect one function binded on 'sl-block-reload' event", function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        events = $('.sl-block').data('events')['sl-block-reload'];
        assert.strictEqual(1, events.length);
        assert.isObject(events[0]);

    });

    test("Expect one function binded on 'sl-block-reloaded' event", function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        events = $('.sl-block').data('events')['sl-block-reload'];
        assert.strictEqual(1, events.length);
        assert.isObject(events[0]);

    });



    test("jQuery masonry is loaded on blocks", function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        assert.isTrue($('.sl-block').hasClass('masonry-brick'));

    });

    test("jQuery resizable is loaded on blocks with handler e, s and es", function(){
        $('.simplelayout')
            .simplelayout('init', {'editable': true})
            .simplelayout('layout');

        assert.isTrue($('.sl-block').hasClass('ui-resizable'));
        assert.isTrue($('.sl-block div').hasClass('ui-resizable-e'));
        assert.isTrue($('.sl-block div').hasClass('ui-resizable-s'));
        assert.isTrue($('.sl-block div').hasClass('ui-resizable-se'));

    });



    teardown(function() {
        $('.simplelayout-page-controls').remove();
        $('.simplelayout').remove();
    });


});