from ftw.simplelayout import _
from ftw.simplelayout.interfaces import ISimplelayoutDefaultSettings
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from z3c.form import form


class SimplelayoutDefaultSettingsForm(RegistryEditForm):
    form.extends(RegistryEditForm)
    schema = ISimplelayoutDefaultSettings

SimplelayoutDefaultSettingsView = layout.wrap_form(
    SimplelayoutDefaultSettingsForm,
    ControlPanelFormWrapper)
SimplelayoutDefaultSettingsView.label = _(u'Simplelayout settings')
