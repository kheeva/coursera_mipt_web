from django.urls import reverse_lazy
from django.views.generic import FormView
from django.http import HttpResponse

from .models import Setting
from .form import ControllerForm
from .tasks import get_sensors_data, smart_home_manager, update_sensors_data

# to delete
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# end delete


# @method_decorator(csrf_exempt, name='dispatch')
class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')
    bed_controller_name = 'bedroom_target_temperature'
    bath_controller_name = 'hot_water_target_temperature'
    bed_light = 'bedroom_light'
    bath_light = 'bathroom_light'
    context_data = {}

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = self.context_data
        return context

    def get_initial(self):
        initial = super(ControllerView, self).get_initial()

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

        sensors_data = get_sensors_data()
        if sensors_data:
            sensors_data = sensors_data['data']
        else:
            return HttpResponse(status=502)

        for sensor in sensors_data:
            self.context_data[sensor['name']] = sensor['value']

        bed_light = self.context_data[self.bed_light]
        bath_light = self.context_data[self.bath_light]

        initial[self.bed_controller_name] = Setting.objects.get(
            controller_name=self.bed_controller_name).value
        initial[self.bath_controller_name] = Setting.objects.get(
            controller_name=self.bath_controller_name).value
        initial[self.bed_light] = bed_light
        initial[self.bath_light] = bath_light

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
            update_sensors_data(lights_updated)

        if settings_updated:
            smart_home_manager()

    def form_valid(self, form):
        self.update_settings(form)
        return super(ControllerView, self).form_valid(form)
