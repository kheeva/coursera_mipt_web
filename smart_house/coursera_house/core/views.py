from django.urls import reverse_lazy
from django.views.generic import FormView
from django.http import HttpResponse

from .models import Setting
from .form import ControllerForm
from .tasks import get_sensors_data, smart_home_manager, update_sensors_data


class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')
    bed_controller_name = 'bedroom_target_temperature'
    bath_controller_name = 'hot_water_target_temperature'
    bed_light = 'bedroom_light'
    bath_light = 'bathroom_light'
    context_data = {}

    def get(self, request, *args, **kwargs):
        """Handle GET requests: instantiate a blank version of the form."""
        sensors_data = get_sensors_data()
        if sensors_data:
            sensors_data = sensors_data['data']
        else:
            return HttpResponse(status=502)

        for sensor in sensors_data:
            self.context_data[sensor['name']] = sensor['value']

        if not Setting.objects.filter(controller_name=self.bed_controller_name):
            bedroom_setting = Setting(
                controller_name=self.bed_controller_name,
                label='Желаемая температура в спальне',
                value=21)
            bedroom_setting.save()

        if not Setting.objects.filter(controller_name=self.bath_controller_name):
            bathroom_setting = Setting(
                controller_name=self.bath_controller_name,
                label='Желаемая температура горячей воды',
                value=80)
            bathroom_setting.save()

        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            update_status = self.update_settings(form)
            if update_status == 502:
                return HttpResponse(status=502)
            else:
                return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = self.context_data
        return context

    def get_initial(self):
        initial = super(ControllerView, self).get_initial()
        initial[self.bed_controller_name] = Setting.objects.get(
            controller_name=self.bed_controller_name).value
        initial[self.bath_controller_name] = Setting.objects.get(
            controller_name=self.bath_controller_name).value
        initial[self.bed_light] = self.context_data[self.bed_light]
        initial[self.bath_light] = self.context_data[self.bath_light]
        return initial

    def update_settings(self, form):
        initial_data = form.initial
        posted_data = form.cleaned_data
        settings_updated = 0
        lights_updated = {}

        if posted_data[self.bed_controller_name] != initial_data[self.bed_controller_name]:
            Setting.objects.filter(controller_name=self.bed_controller_name).update(
                value=posted_data[self.bed_controller_name])
            settings_updated = 1

        if posted_data[self.bath_controller_name] != initial_data[self.bath_controller_name]:
            Setting.objects.filter(controller_name=self.bath_controller_name).update(
                value=posted_data[self.bath_controller_name])
            settings_updated = 1

        if posted_data[self.bed_light] != initial_data[self.bed_light]:
            if posted_data[self.bed_light]:
                if not self.context_data['smoke_detector']:
                    lights_updated[self.bed_light] = posted_data[self.bed_light]
            else:
                lights_updated[self.bed_light] = posted_data[self.bed_light]

        if posted_data[self.bath_light] != initial_data[self.bath_light]:
            if posted_data[self.bath_light]:
                if not self.context_data['smoke_detector']:
                    lights_updated[self.bath_light] = posted_data[self.bath_light]
            else:
                lights_updated[self.bath_light] = posted_data[self.bath_light]

        if lights_updated:
            update_status = update_sensors_data(lights_updated)
            if update_status != 200:
                return 502

        if settings_updated:
            manager_response = smart_home_manager()
            if manager_response != 200:
                return 502
        return 200

    def form_valid(self, form):
        return super(ControllerView, self).form_valid(form)
