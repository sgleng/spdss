from django.contrib import admin
from .models import Skills,Tasks,Projects,Workers,Shifts,Availability,WorkerSkills
from datetime import date

class TaskInline(admin.ModelAdmin):
	list_display = ('name', 'project', 'due_date', 'status')
	list_filter = ['project__name']

class ProjectInline(admin.ModelAdmin):
	list_display = ('name', 'due_date', 'status', 'overdue')
	list_filter = ['status']
	def overdue(self, obj):
		return(date.today() - obj.due_date)

class WorkerSkillsInline(admin.ModelAdmin):
	list_display = ('worker', 'skill', 'productivity')
	list_filter = ['worker__name', 'skill__name']

class ShiftsInline(admin.ModelAdmin):
	list_display = ('name', 'length')

class AvailabilityInline(admin.ModelAdmin):
	list_display = ('worker', 'date')
	list_filter = ['worker__name', 'date']

admin.site.register(Shifts,ShiftsInline)
admin.site.register(Workers)
admin.site.register(Availability,AvailabilityInline)
admin.site.register(Skills)
admin.site.register(WorkerSkills,WorkerSkillsInline)
admin.site.register(Tasks, TaskInline)
admin.site.register(Projects,ProjectInline)