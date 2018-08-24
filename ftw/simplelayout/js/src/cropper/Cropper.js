let Cropperjs = require("cropperjs");
import $ from "jquery";


class ToolbarButton {
    constructor(element) {
        this.element = $(element)
    }

    render(props = {}) {
        this.element.off('click')
        this.element.on('click', props.onClick);
        let container = this.element.parent('li')
        props.active ? container.addClass('active') : container.removeClass('active')
    }
}

export default class Cropper {
    constructor(imageCropperWrapper) {
        this.btnDragModeMove = new ToolbarButton($('.btnDragModeMove', this.wrapper));
        this.btnDragModeCrop = new ToolbarButton($('.btnDragModeCrop', this.wrapper));

        this.btnZoomIn = new ToolbarButton($('.btnZoomIn', this.wrapper));
        this.btnZoomOut = new ToolbarButton($('.btnZoomOut', this.wrapper));

        this.btnAspectRatios = []
        $('.btnAspectRatioButton', this.wrapper).each((index, element) => {
            this.btnAspectRatios.push(new ToolbarButton(element));
        });

        this.btnClear = new ToolbarButton($('.btnClear', this.wrapper));

        this.state = {
            dragMode: 'crop',
            aspectRatio: this.getDefaultAspectRatio()
        };

        this.wrapper = $(imageCropperWrapper);
        this.originalImage = $('.croppingImage', $(imageCropperWrapper)).get(0);

        this.cropper = null

        imageCropperWrapper.slcropper = this;
    }

    run() {
        let config = this.wrapper.data('config');
        let { aspectRatio } = this.getState()

        let self = this;
        this.cropper = new Cropperjs(this.originalImage,  {
            viewMode: 1,
            aspectRatio,
            ready() {
                this.cropper.setData(config);
                self.render()
            }
        });
    }

    getState() {
        return {...this.state}
    }

    setState(callback) {
        this.state = {
            ...this.state,
            ...callback(this.getState())
        };

        this.render();
    }

    getDefaultAspectRatio() {
        return this.btnAspectRatios.length > 0
            ? this.btnAspectRatios[0].element.data('value')
            : 0
    }

    setDragMode(mode) {
        this.setState(() => ({ dragMode: mode }));
    }

    zoomIn() {
        this.cropper.zoom(0.1);
    }

    zoomOut() {
        this.cropper.zoom(-0.1);
    }

    setAspectRatio(aspectRatio) {
        this.cropper.setAspectRatio(aspectRatio);
        this.setState(() => ({ aspectRatio }));
    }

    clear() {
        this.cropper.clear();
    }

    render() {
        let { dragMode, aspectRatio } = this.getState();

        this.cropper.setDragMode(dragMode);

        this.btnDragModeMove.render({
            active: dragMode === 'move',
            onClick: () => this.setDragMode('move')
        });

        this.btnDragModeCrop.render({
            active: dragMode === 'crop',
            onClick: () => this.setDragMode('crop')
        });

        this.btnZoomIn.render({
            onClick: () => this.zoomIn()
        });

        this.btnZoomOut.render({
            onClick: () => this.zoomOut()
        });

        this.btnAspectRatios.forEach((button) => {
            let ratio = button.element.data('value');
            button.render({
                active: aspectRatio === ratio,
                onClick: () => this.setAspectRatio(ratio)
            });
        });

        this.btnClear.render({
            onClick: () => this.clear()
        });
    }

    processFormData(formData) {
        formData.append('is_cropped', this.cropper.cropped);
        formData.append('cropped_config', JSON.stringify(this.cropper.getData()));
        formData.append('cropped_image_data', this.cropper.getCroppedCanvas().toDataURL('image/jpeg'));
    }
}
