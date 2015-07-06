from collective.quickupload.browser import uploadcapable


class FileListingQuickUploadCapableFileFactory(
        uploadcapable.QuickUploadCapableFileFactory):

    def __call__(self, filename, title, description, content_type,
                 data, portal_type):

        portal_type = "File"
        return super(FileListingQuickUploadCapableFileFactory, self).__call__(
            filename, title, description, content_type, data, portal_type)
