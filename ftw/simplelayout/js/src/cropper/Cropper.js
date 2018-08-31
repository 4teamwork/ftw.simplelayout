import Cropperjs from "cropperjs";
import Handlebars from "handlebars";
import $ from "jquery";


class Button {
    constructor(element) {
        this.element = $(element);
    }

    render(props = {}) {
        props.disabled ? this.element.prop("disabled",true) : this.element.prop("disabled", false);
    }
}

class ToolbarButton {
    constructor(element) {
        this.element = $(element);
    }

    render(props = {}) {
        this.element.off('click');
        this.element.on('click', props.onClick);
        let container = this.element.parent('li');
        props.active ? container.addClass('active') : container.removeClass('active');
    }
}

export default class Cropper {
    constructor(imageCropperWrapper) {
        this.HARD_LIMIT_IDENTIFIER = 'hard';
        this.SOFT_LIMIT_IDENTIFIER = 'soft';

        this.wrapper = $(imageCropperWrapper);
        this.config = this.wrapper.data('config');

        this.originalImage = $('.croppingImage', $(imageCropperWrapper)).get(0);

        this.btnDragModeMove = new ToolbarButton($('.btnDragModeMove', this.wrapper));
        this.btnDragModeCrop = new ToolbarButton($('.btnDragModeCrop', this.wrapper));

        this.btnZoomIn = new ToolbarButton($('.btnZoomIn', this.wrapper));
        this.btnZoomOut = new ToolbarButton($('.btnZoomOut', this.wrapper));

        this.btnAspectRatios = [];
        $('.btnAspectRatioButton', this.wrapper).each((index, element) => {
            this.btnAspectRatios.push(new ToolbarButton(element));
        });

        this.btnClear = new ToolbarButton($('.btnClear', this.wrapper));

        this.btnSave = new Button($('.btnSave', this.wrapper));

        this.validationMessageContainer = document.getElementById(
            "image-cropper-validation-message-container");

        this.hardLimitValidationTemplate = Handlebars.compile(
            document.getElementById("hard-limit-validation-template").innerHTML);

        this.softLimitValidationTemplate = Handlebars.compile(
            document.getElementById("soft-limit-validation-template").innerHTML);


        this.state = {
            dragMode: 'crop',
            aspectRatio: this.getDefaultAspectRatio(),
            limits: this.config.limits,
            allowSave: true,
            showLimitValidation: '',
        };

        this.cropper = null;

        imageCropperWrapper.slcropper = this;
    }

    run() {
        let { aspectRatio } = this.getState();
        let { cropperData } = this.config.cropped_config;

        let self = this;
        this.cropper = new Cropperjs(this.originalImage,  {
            autoCrop: cropperData !== undefined,
            viewMode: 1,
            aspectRatio,
            ready() {
                this.cropper.setData(cropperData);
                self.render()
            },
            crop() {
                self.validateLimits();
            }
        });
    }

    getState() {
        return {...this.state};
    }

    setState(callback) {
        this.state = {
            ...this.state,
            ...callback(this.getState())
        };

        this.render();
    }

    validateLimits() {
        this.validationMessageContainer.innerHTML = ''
        if (this.validateHardLimit() && this.validateSoftLimit()) {
            this.setState(() => ({
                showLimitValidation: false,
                allowSave: true
            }));
        };
    }

    validateSoftLimit() {
        let { limits } = this.getState();
        let { width, height } = this.cropper.getData();
        let { cropped } = this.cropper;

        if (!cropped) {
            return true;
        }

        if (width < limits.soft.width || height < limits.soft.height) {
            this.setState(() => ({
                showLimitValidation: this.SOFT_LIMIT_IDENTIFIER,
                allowSave: true
            }));
            return false;
        }
        return true;
    }

    validateHardLimit() {
        let { limits } = this.getState();
        let { width, height } = this.cropper.getData();
        let { cropped } = this.cropper;

        if (!cropped) {
            return true;
        }

        if (width < limits.hard.width || height < limits.hard.height) {
            this.setState(() => ({
                showLimitValidation: this.HARD_LIMIT_IDENTIFIER,
                allowSave: false
            }));
            return false;
        };
        return true;
    }

    handleLimitValidationMessage() {
        let { showLimitValidation, limits } = this.getState();
        let { width, height } = this.cropper.getData();

        switch (showLimitValidation) {
            case this.SOFT_LIMIT_IDENTIFIER:
                this.showLimitValidationMessage(
                    this.softLimitValidationTemplate,
                    width, limits.soft.width, height, limits.soft.height);

                break;

            case this.HARD_LIMIT_IDENTIFIER:
                this.showLimitValidationMessage(
                    this.hardLimitValidationTemplate,
                    width, limits.hard.width, height, limits.hard.height);

                break;
        }
    }

    showLimitValidationMessage(template, width, limitWidth, height, limitHeight) {

        this.validationMessageContainer.innerHTML = template(
            {
                currentWidth: Math.round(width),
                limitWidth,
                currentHeight: Math.round(height),
                limitHeight
            }
        );
    }

    getDefaultAspectRatio() {
        let { currentAspectRatio } = this.config.cropped_config;

        if ( typeof currentAspectRatio !== 'undefined') { return currentAspectRatio };
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

    allowSave() {
        let { showLimitValidation } = this.getState();
        let { cropped } = this.cropper;

        if (cropped && showLimitValidation == this.HARD_LIMIT_IDENTIFIER) {
            return false;
        }
        return true;
    }
    render() {
        let { dragMode, aspectRatio, allowSave } = this.getState();

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

        this.btnSave.render({
            disabled: !this.allowSave()
        });

        this.handleLimitValidationMessage();

    }

    processFormData(formData) {
        let { aspectRatio } = this.getState();

        formData.append('is_cropped', this.cropper.cropped);
        formData.append('cropped_config', JSON.stringify({
            cropperData: this.cropper.getData(),
            currentAspectRatio: aspectRatio }));
        formData.append('cropped_image_data', this.cropper.getCroppedCanvas().toDataURL('image/jpeg'));
    }
}
