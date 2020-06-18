from django import forms
from .models import Workers,WorkerSkills,Skills,Availability,Tasks

class PlanningForm(forms.Form):
	date = forms.ChoiceField(label='Date', choices=[])


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['date'].choices = [(avb['date'], avb['date']) for avb in Availability.objects.values('date').distinct().order_by('-date')]
		skills = Skills.objects.all()
		for skill in skills:
			self.fields["min_" + skill.name] = forms.FloatField(label="Minimum output for " + skill.name, help_text="Zero is no minimum.", initial=0)
			self.fields["max_" + skill.name] = forms.FloatField(label="Maximum output for " + skill.name, help_text="Default is set to open outstanding tasks for this skill.", initial=Tasks.objects.filter(skills=skill.id,status=0).count())
