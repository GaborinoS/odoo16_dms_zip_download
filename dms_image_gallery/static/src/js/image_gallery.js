odoo.define('dms_image_gallery.ImageGallery', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var ajax = require('web.ajax');

    var QWeb = core.qweb;
    var _t = core._t;

    var DmsImageGallery = AbstractAction.extend({
        template: 'dms_image_gallery.DmsImageGallery',  // Updated to match the XML template name
        events: {
            'click .o_dms_image_prev': '_onPrevImage',
            'click .o_dms_image_next': '_onNextImage',
            'click .o_dms_image_zoom_in': '_onZoomIn',
            'click .o_dms_image_zoom_out': '_onZoomOut',
            'click .o_dms_image_zoom_reset': '_onZoomReset',
            'click .o_dms_image_slideshow': '_onSlideshow',
            'click .o_dms_image_download': '_onDownload',
            'click .o_dms_image_close': '_onClose',
            'click .o_dms_image_thumbnail': '_onThumbnailClick',
            'dblclick .o_dms_image_main': '_onImageDblClick',
            'wheel .o_dms_image_gallery_container': '_onMouseWheel',
        },
        
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.fileId = action.params.file_id;
            this.directoryId = action.params.directory_id;
            this.fileName = action.params.file_name;
            
            this.images = [];
            this.currentImageId = this.fileId;
            this.currentImageIndex = 0;
            this.currentImageName = this.fileName;
            this.currentImageUrl = '/dms_image_gallery/image_content/' + this.fileId;
            
            this.zoomLevel = 1.0;
            this.slideShowInterval = null;
            this.slideShowDelay = 5000; // 5 seconds
            this.isSlideshowActive = false;
        },
        
        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._loadImages();
            });
        },
        
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._resizeContent();
                
                // Handle keyboard shortcuts
                $(document).on('keydown.dms_gallery', function (e) {
                    if (e.keyCode === 37) { // Left arrow
                        self._onPrevImage();
                    } else if (e.keyCode === 39) { // Right arrow
                        self._onNextImage();
                    } else if (e.keyCode === 27) { // Escape
                        self._onClose();
                    } else if (e.keyCode === 32) { // Space
                        self._onSlideshow();
                        e.preventDefault();
                    }
                });
                
                // Handle window resize
                $(window).on('resize.dms_gallery', _.debounce(function () {
                    self._resizeContent();
                }, 200));
            });
        },
        
        destroy: function () {
            $(document).off('keydown.dms_gallery');
            $(window).off('resize.dms_gallery');
            if (this.slideShowInterval) {
                clearInterval(this.slideShowInterval);
            }
            this._super.apply(this, arguments);
        },
        
        _loadImages: function () {
            var self = this;
            return ajax.jsonRpc('/dms_image_gallery/directory_images/' + this.directoryId, 'call', {})
                .then(function (result) {
                    if (result.error) {
                        self.displayNotification({
                            title: _t('Error'),
                            message: result.error,
                            type: 'danger'
                        });
                        return Promise.reject(result.error);
                    }
                    
                    self.images = result;
                    
                    // Find the index of the current image
                    self.currentImageIndex = _.findIndex(self.images, function (img) {
                        return img.id === self.fileId;
                    });
                    
                    if (self.currentImageIndex === -1) {
                        self.currentImageIndex = 0;
                        if (self.images.length > 0) {
                            self.currentImageId = self.images[0].id;
                            self.currentImageName = self.images[0].name;
                            self.currentImageUrl = self.images[0].url;
                        }
                    }
                });
        },
        
        _resizeContent: function () {
            var height = $(window).height() - 
                this.$('.o_dms_image_gallery_header').outerHeight() - 
                this.$('.o_dms_image_gallery_footer').outerHeight() - 
                40; // Extra padding
            
            this.$('.o_dms_image_gallery_content').css('height', height + 'px');
        },
        
        _showImage: function (index) {
            if (index < 0) {
                index = this.images.length - 1;
            } else if (index >= this.images.length) {
                index = 0;
            }
            
            this.currentImageIndex = index;
            this.currentImageId = this.images[index].id;
            this.currentImageName = this.images[index].name;
            this.currentImageUrl = this.images[index].url;
            
            // Update UI
            this.$('.o_dms_image_main').attr('src', this.currentImageUrl);
            this.$('.o_dms_image_gallery_title').html(
                this.currentImageName + ' <span class="text-muted">(' + 
                (this.currentImageIndex + 1) + '/' + this.images.length + ')</span>'
            );
            
            // Update thumbnails
            this.$('.o_dms_image_thumbnail').removeClass('active');
            this.$(`.o_dms_image_thumbnail[data-id="${this.currentImageId}"]`).addClass('active');
            
            // Scroll thumbnail into view
            var $activeThumb = this.$(`.o_dms_image_thumbnail[data-id="${this.currentImageId}"]`);
            if ($activeThumb.length) {
                var $thumbnailsContainer = this.$('.o_dms_image_thumbnails');
                $thumbnailsContainer.scrollLeft(
                    $activeThumb.position().left + $thumbnailsContainer.scrollLeft() - 
                    $thumbnailsContainer.width()/2 + $activeThumb.width()/2
                );
            }
            
            // Reset zoom
            this._onZoomReset();
        },
        
        _onPrevImage: function () {
            this._showImage(this.currentImageIndex - 1);
        },
        
        _onNextImage: function () {
            this._showImage(this.currentImageIndex + 1);
        },
        
        _onZoomIn: function () {
            this.zoomLevel = Math.min(5.0, this.zoomLevel + 0.25);
            this._applyZoom();
        },
        
        _onZoomOut: function () {
            this.zoomLevel = Math.max(0.25, this.zoomLevel - 0.25);
            this._applyZoom();
        },
        
        _onZoomReset: function () {
            this.zoomLevel = 1.0;
            this._applyZoom();
        },
        
        _applyZoom: function () {
            this.$('.o_dms_image_main').css({
                'transform': 'scale(' + this.zoomLevel + ')',
                'transform-origin': 'center center'
            });
        },
        
        _onSlideshow: function () {
            var self = this;
            
            if (this.isSlideshowActive) {
                // Stop slideshow
                clearInterval(this.slideShowInterval);
                this.slideShowInterval = null;
                this.isSlideshowActive = false;
                this.$('.o_dms_image_slideshow i').removeClass('fa-pause').addClass('fa-play');
            } else {
                // Start slideshow
                this.isSlideshowActive = true;
                this.$('.o_dms_image_slideshow i').removeClass('fa-play').addClass('fa-pause');
                
                // Show next image immediately
                this._onNextImage();
                
                // Set interval for automatic navigation
                this.slideShowInterval = setInterval(function () {
                    self._onNextImage();
                }, this.slideShowDelay);
            }
        },
        
        _onDownload: function () {
            window.location = '/web/content/' + 
                '?model=dms.file' + 
                '&id=' + this.currentImageId + 
                '&field=content' + 
                '&filename_field=name' + 
                '&download=true';
        },
        
        _onClose: function () {
            if (this.slideShowInterval) {
                clearInterval(this.slideShowInterval);
            }
            this.trigger_up('history_back');
        },
        
        _onThumbnailClick: function (ev) {
            var imageId = $(ev.currentTarget).data('id');
            var index = _.findIndex(this.images, function (img) {
                return img.id === imageId;
            });
            
            if (index !== -1) {
                this._showImage(index);
            }
        },
        
        _onImageDblClick: function (ev) {
            if (this.zoomLevel === 1.0) {
                this._onZoomIn();
            } else {
                this._onZoomReset();
            }
        },
        
        _onMouseWheel: function (ev) {
            // Prevent default scrolling
            ev.preventDefault();
            
            if (ev.originalEvent.deltaY < 0) {
                // Scroll up - zoom in
                this._onZoomIn();
            } else {
                // Scroll down - zoom out
                this._onZoomOut();
            }
        }
    });

    core.action_registry.add('dms_image_gallery', DmsImageGallery);

    return DmsImageGallery;
});