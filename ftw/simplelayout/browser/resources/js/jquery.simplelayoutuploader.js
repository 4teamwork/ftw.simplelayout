(function($) {

    $.fn.simplelayoutuploader = function(options) {

        var files;
        var settings;
        var $destination;

        function prepare_form_data(file, form_data_callback){
            var form_data = new FormData();
            form_data.append('file', file);
            form_data.append('filename', file.name);

            if (typeof form_data_callback === "function"){
                form_data_callback(file, form_data);
            }
            return form_data;
        }

        function create_status_bar(statuscontainer) {
            this.statusbar = $('<div class="statusbar"></div>');
            this.progress_bar = $("<div class='progressBar'><div></div></div>").appendTo(this.statusbar);
            $(statuscontainer, $destination).html(this.statusbar);

            this.set_progress = function(progress) {
                var progress_bar_width = progress * this.progress_bar.width() / 100;
                this.progress_bar.find('div').animate({
                    width: progress_bar_width
                }, 10).html(progress + "% ");
            };
        }

        function upload($destinations){
            $destination = $destinations;

            // If upload is called on multiple objects get the right upload element.
            if ($destinations.length !== 1) {
                $destination = $destinations.eq($destinations.length - files.length);
            }

            var file = files.pop();
            var status = new create_status_bar(settings.statuscontainer);
            form_data = prepare_form_data(file, settings.form_data_callback);

            var $xhr = $.ajax({
                xhr: function() {
                    var xhrobj = $.ajaxSettings.xhr();
                    if (xhrobj.upload) {
                        xhrobj.upload.addEventListener('progress', function(e) {
                            var percent = 0;
                            var position = e.loaded || e.position;
                            var total = e.total;
                            if (e.lengthComputable) {
                                percent = Math.ceil(position / total * 100);
                            }
                            //Set progress
                            status.set_progress(percent);
                        }, false);
                    }
                    return xhrobj;
                },
                url: settings.uploadurl,
                type: 'POST',
                contentType: false,
                processData: false,
                cache: false,
                async: true,
                data: form_data,
                success: function(data) {
                    status.set_progress(100);

                    if (typeof settings.upload_success_each === 'function'){
                        settings.upload_success_each($destination, data);
                    }

                    if (files.length === 0) {
                        if (typeof settings.upload_success_all === 'function'){
                            settings.upload_success_all($destination, data);
                        }

                    } else {
                        upload($destinations);
                    }

                },
                error: function(xhr, status, error) {
                    alert(status, error);
                }
            });

        }


        var methods = {
            init: function(options) {
                var defaults = {
                    files: null,
                    uploadurl: './sl-ajax-file-upload',
                    upload_success_all: null,
                    upload_success_each: null,
                    statuscontainer: null,
                    form_data_callback: null
                };

                settings = $.extend({}, defaults, options);
                if (settings.files === null){ return; }

                files = settings.files;
                files.reverse();

                upload($(this));
            }

        };

        var method = arguments[0];

        if (methods[method]) {
            method = methods[method];
            arguments = Array.prototype.slice.call(arguments, 1);
        } else if (typeof(method) == 'object' || !method) {
            method = methods.init;
        } else {
            $.error('Method ' + method + ' does not exist on jQuery.pluginName');
            return this;
        }

        return method.apply(this, arguments);

    };
})(jQuery);
