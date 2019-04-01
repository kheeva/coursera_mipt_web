from django.urls import reverse_lazy
from django.views.generic import FormView

from .models import Setting
from .form import ControllerForm

# to delete
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
# end delete


# @method_decorator(csrf_exempt, name='dispatch')
class ControllerView(FormView):
    form_class = ControllerForm
    template_name = 'core/control.html'
    success_url = reverse_lazy('form')

    def get_context_data(self, **kwargs):
        context = super(ControllerView, self).get_context_data()
        context['data'] = {'test': 'test'}
        return context

    def get_initial(self):
        initial = super(ControllerView, self).get_initial()
        bed_label = 'bedroom_target_temperature'
        initial[bed_label] = Setting.objects.get(label=bed_label).value
        bath_label = 'hot_water_target_temperature'
        initial[bath_label] = Setting.objects.get(label=bath_label).value
        return initial

    def update_settings(self, form):
        bed_label = 'bedroom_target_temperature'
        stored_bedroom_temp = Setting.objects.get(label=bed_label).value
        form_bedroom_temp = int(form.data[bed_label])
        if stored_bedroom_temp != form_bedroom_temp:
            print(
                f'stored - {stored_bedroom_temp} \n from form - {form_bedroom_temp}')
            Setting.objects.filter(label=bed_label).update(
                value=form_bedroom_temp)

        bath_label = 'hot_water_target_temperature'
        stored_bathroom_temp = Setting.objects.get(label=bath_label).value
        form_bathroom_temp = int(form.data[bath_label])
        if stored_bathroom_temp != form_bathroom_temp:
            print(
                f'stored - {stored_bathroom_temp} \n from form - {form_bathroom_temp}')
            Setting.objects.filter(label=bath_label).update(
                value=form_bathroom_temp)

    def form_valid(self, form):
        print(form.cleaned_data)
        print(form.changed_data)
        print(form.initial)
        # print(dir(form))
        # self.update_settings(form)
        return super(ControllerView, self).form_valid(form)
