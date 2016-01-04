suite("Toolbar", function() {
  "use strict";

  var Toolbar;

  suiteSetup(function(done) {
    require(["app/simplelayout/Toolbar"], function(_Toolbar) {
      Toolbar = _Toolbar;
      done();
    });
  });

  test("is a constructor function", function() {
    assert.throw(Toolbar, TypeError, "Toolbar constructor cannot be called as a function.");
  });

  test("can add a edit action", function() {
    var toolbar = new Toolbar({edit: {"class": "edit icon-edit", "title": "Can edit this block"}});
    var actionNodes = $.map(toolbar.element.find("a"), function(action) {
      return {tagName: action.tagName, classes: action.className, title: action.title};
    });

    assert.deepEqual(actionNodes, [{tagName: "A", classes: "edit icon-edit", title: "Can edit this block"}]);
  });

  test("can disable or enable an action", function() {
    var toolbar = new Toolbar({edit: {"class": "edit icon-edit", "title": "Can edit this block"}});
    toolbar.disable("edit");
    var actionNodes = $.map(toolbar.element.find("a"), function(action) {
      return {tagName: action.tagName, classes: action.className, title: action.title, display: action.style.display};
    });

    assert.deepEqual(actionNodes, [{tagName: "A", classes: "edit icon-edit", title: "Can edit this block", display: "none"}]);

    toolbar.enable("edit");

    actionNodes = $.map(toolbar.element.find("a"), function(action) {
      return {tagName: action.tagName, classes: action.className, title: action.title, display: action.style.display};
    });

    assert.deepEqual(actionNodes, [{tagName: "A", classes: "edit icon-edit", title: "Can edit this block", display: "inline"}]);
  });

});
