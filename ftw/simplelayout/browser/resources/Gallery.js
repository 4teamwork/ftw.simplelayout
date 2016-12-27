(function(global, HBS, Showroom) {

  function Gallery(target) {

    var items = target.querySelectorAll(".gallery-item");

    var template = HBS.compile('\
      <div class="{{showroom.options.cssClass}} ftw-gallery">\
        <figure>\
          <img width="{{image.width}}px" height="{{image.height}}px" src="{{image.url}}" />\
          <figcaption class="gallery-caption">\
            <span class="gallery-pagenumber">{{showroom.current}}/{{showroom.options.total}} | </span>\
            <h1 class="gallery-title">{{item.title}}</h1>\
          </figcaption>\
          <button class="ftw-showroom-close"></button>\
          <button class="button-gallery button-gallery-next ftw-showroom-next"></button>\
          <button class="button-gallery button-gallery-prev ftw-showroom-prev"></button>\
        </figure>\
      </div>\
    ');

    function render(image) { return $(template({ showroom: showroom, image: image, item: showroom.items[showroom.current - 1] })); }

    function fetch(item) { return JSON.parse(item.target); }

    function refresh() {
      items = target.querySelectorAll(".gallery-item");
      showroom.reset(items);
      showroom.setTotal(items.length);
    }

    var showroom = Showroom(items, {
      render: render,
      fetch: fetch,
      total: items.length
    });

    return Object.freeze({ refresh: refresh });

  }

  global.Gallery = Gallery;

  $(function() {
    [].slice.call(document.querySelectorAll(".ftw-simplelayout-galleryblock")).map(function(galleryblock) {
      var gallery = Gallery(galleryblock);
      $(galleryblock).data("gallery", gallery);
    });
  });

})(window, window.Handlebars, window.ftw.showroom);
