from django.urls import reverse_lazy
from django.views.generic import FormView

from .models import Setting
from .form import ControllerForm
from .tasks import get_sensors_data

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

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        sensors_data = get_sensors_data()['data']
        context['data'] = {}
        for sensor in sensors_data:
            context['data'][sensor['name']] = sensor['value']
        return context

    def get_initial(self):
        initial = super(ControllerView, self).get_initial()

        if not Setting.objects.filter(label=self.bed_label):
            bedroom_setting = Setting(
                controller_name='Oleg Ivliev \'s smart house',
                label=self.bed_label,
                value=21)
            bedroom_setting.save()

        if not Setting.objects.filter(label=self.bath_label):
            bathroom_setting = Setting(
                controller_name='Oleg Ivliev \'s smart house',
                label=self.bath_label,
                value=80)
            bathroom_setting.save()

        initial[self.bed_label] = Setting.objects.get(
            label=self.bed_label).value
        initial[self.bath_label] = Setting.objects.get(
            label=self.bath_label).value

        return initial

    def update_settings(self, form):
        initial_data = form.initial
        posted_data = form.cleaned_data
        if posted_data[self.bed_label] != initial_data[self.bed_label]:
            Setting.objects.filter(label=self.bed_label).update(
                value=posted_data[self.bed_label])

        if posted_data[self.bath_label] != initial_data[self.bath_label]:
            Setting.objects.filter(label=self.bath_label).update(
                value=posted_data[self.bath_label])


    def form_valid(self, form):
        self.update_settings(form)
        return super(ControllerView, self).form_valid(form)
