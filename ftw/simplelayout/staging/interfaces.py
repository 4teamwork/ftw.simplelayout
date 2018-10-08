from zope.interface import Interface


class IStaging(Interface):
    """The staging adapter provides functionality for implementing and controlling staging.

    It adapts a future baseline, a baseline or a working copy.
    """

    def __init__(context, request):
        pass

    def create_working_copy(target_container):
        """Create a copy of the currently adapted object in the target_container folder.
        Return the working copy object.
        """


class IBaseline(Interface):
    """Marker interface for baseline objects.
    A baseline object is an object of which a working copy exists.
    """


class IWorkingCopy(Interface):
    """Marker interface for working copy objects.
    """
