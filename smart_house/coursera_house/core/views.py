from django.urls import reverse_lazy
from django.views.generic import FormView

from .models import Setting
from .form import ControllerForm
from .tasks import get_sensors_data, smart_home_manager

# to delete
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# end delete


# @method_decorator(csrf_exempt, name='dispatch')
class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')
    bed_label = 'bedroom_target_temperature'
    bath_label = 'hot_water_target_temperature'
    bed_light = 'bedroom_light'
    bath_light = 'bathroom_light'
    context_data = {}

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = self.context_data
        return context

    def get_initial(self):
        initial = super(ControllerView, self).get_initial()

        if not Setting.objects.filter(label=self.bed_label):
            bedroom_setting = Setting(
                controller_name=self.bed_label,
                label=self.bed_label,
                value=21)
            bedroom_setting.save()

        if not Setting.objects.filter(label=self.bath_label):
            bathroom_setting = Setting(
                controller_name=self.bath_label,
                label=self.bath_label,
                value=80)
            bathroom_setting.save()

        sensors_data = get_sensors_data()['data']

        for sensor in sensors_data:
            self.context_data[sensor['name']] = sensor['value']

        bed_light = self.context_data[self.bed_light]
        bath_light = self.context_data[self.bath_light]

        if not Setting.objects.filter(label=self.bed_light):
            bedroom_light_setting = Setting(
                controller_name=self.bed_light,
                label=self.bed_light,
                value=bed_light)
            bedroom_light_setting.save()

        if not Setting.objects.filter(label=self.bath_light):
            bathroom_light_setting = Setting(
                controller_name=self.bath_light,
                label=self.bath_light,
                value=bath_light)
            bathroom_light_setting.save()

        initial[self.bed_label] = Setting.objects.get(
            label=self.bed_label).value
        initial[self.bath_label] = Setting.objects.get(
            label=self.bath_label).value
        initial[self.bed_light] = bed_light
        initial[self.bath_light] = bath_light

        return initial

    def update_settings(self, form):
        initial_data = form.initial
        posted_data = form.cleaned_data
        settings_updated = 0

        if posted_data[self.bed_label] != initial_data[self.bed_label]:
            Setting.objects.filter(label=self.bed_label).update(
                value=posted_data[self.bed_label])
            settings_updated = 1

        if posted_data[self.bath_label] != initial_data[self.bath_label]:
            Setting.objects.filter(label=self.bath_label).update(
                value=posted_data[self.bath_label])
            settings_updated = 1

        if posted_data[self.bed_light] != initial_data[self.bed_light]:
            Setting.objects.filter(label=self.bed_light).update(
                value=posted_data[self.bed_light])
            settings_updated = 1

        if posted_data[self.bath_light] != initial_data[self.bath_light]:
            Setting.objects.filter(label=self.bath_light).update(
                value=posted_data[self.bath_light])
            settings_updated = 1

        if settings_updated:
            smart_home_manager()

    def form_valid(self, form):
        self.update_settings(form)
        return super(ControllerView, self).form_valid(form)
