from django.db import models

# This file contains the database structure of this project.
# It contains different tables.

class Skills(models.Model):
	name = models.CharField(max_length=50)
	workplaces = models.IntegerField(default=1)
	gross_profit = models.FloatField(default=0)
	class Meta: verbose_name_plural = 'Skills'
	def __str__(self): return self.name
	pass

class Projects(models.Model):
	PRIORITY_CHOICES = [
		(0, 'No priority'),
		(1, 'Low priority'),
		(2, 'Medium priority'),
		(3, 'High priority')
	]
	CLOSED_CHOICES = [
		(0, 'Open'),
		(1, 'Closed')
	]
	name = models.CharField(max_length=50)
	creation_date = models.DateField()
	due_date = models.DateField()
	status = models.IntegerField(default=0, choices=CLOSED_CHOICES)
	priority = models.IntegerField(default=0, choices=PRIORITY_CHOICES)
	class Meta: verbose_name_plural = 'Projects'
	def __str__(self): return self.name
	pass

class Tasks(models.Model):
	# The priority helps in providing assistance for the sequence of the tasks.
	PRIORITY_CHOICES = [
		(0, 'No priority'),
		(1, 'Low priority'),
		(2, 'Medium priority'),
		(3, 'High priority')
	]
	# A task can either be open or closed. A closed task is a finished task.
	CLOSED_CHOICES = [
		(0, 'Open'),
		(1, 'Closed')
	]
	name = models.CharField(max_length=50)
	due_date = models.DateField()
	skills = models.ForeignKey(Skills, on_delete=models.CASCADE) # One task recorresponds to one specific skill.
	project = models.ForeignKey(Projects, on_delete=models.CASCADE) # One task recorresponds to one specific project.
	priority = models.IntegerField(default=0, choices=PRIORITY_CHOICES)
	status = models.IntegerField(default=0, choices=CLOSED_CHOICES)
	class Meta: verbose_name_plural = 'Tasks'
	def __str__(self): return self.name

class Workers(models.Model):
	name = models.CharField(max_length=50)
	preference = models.ForeignKey(Skills, blank=True, null=True, on_delete=models.SET_NULL)
	class Meta: verbose_name_plural = 'Workers'
	def __str__(self): return self.name

class Shifts(models.Model):
	name = models.CharField(max_length=50)
	length = models.FloatField(default=0) # Length in hours, minus breaks
	class Meta: verbose_name_plural = 'Shifts'
	def __str__(self): return self.name

class Availability(models.Model):
	worker = models.ForeignKey(Workers, on_delete=models.PROTECT) # Availability of one date corresponds to one worker.
	date = models.DateField()
	shift = models.ManyToManyField(Shifts) # Availability depends on a shift.
	class Meta: 
		verbose_name_plural = 'Availability'
		unique_together = ('worker', 'date',) # Do not allow to have duplicate availabilities for a worker on a date and a certain shift.

class WorkerSkills(models.Model):
	date = models.DateField()
	worker = models.ForeignKey(Workers, on_delete=models.CASCADE) 
	skill = models.ForeignKey(Skills, on_delete=models.CASCADE) 
	productivity = models.FloatField(default=0)
	def __str__(self):
		return self.skill.name
	class Meta: 
		verbose_name_plural = 'Worker skills'
		unique_together = ('date', 'worker', 'skill',) # Do not allow for the worker to have the multiple skills simultaneously.