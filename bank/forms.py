from django.forms import DateInput, ModelForm, NumberInput

from bank.models import DonationRequest


class DatePickerInput(DateInput):
    input_type = 'date'


class PrivateRequestForm(ModelForm):
    class Meta:
        model = DonationRequest
        exclude = ['createdAt', 'createdBy', 'bloodGroup',
                   'targetDonor', 'acceptedBy', 'cancelled']
        widgets = {
            'date': DatePickerInput()
        }


class PublicRequestForm(ModelForm):
    class Meta:
        model = DonationRequest
        exclude = ['createdAt', 'createdBy',
                   'targetDonor', 'acceptedBy', 'cancelled']
        widgets = {
            'date': DatePickerInput()
        }
