from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import Workers,WorkerSkills,Skills,Projects,Tasks,Availability,Shifts
from .forms import PlanningForm
from django.urls import reverse_lazy,reverse
from django.db.models import Q,Count,Sum
import datetime
from .solver import Optimize
from .solver import ProgressFit
import numpy as np

def home(request):
    if request.user.is_authenticated:
        return render(request, 'planning/dashboard.html')
    else:
        return render(request, 'planning/home.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}. You can now login.')
            return HttpResponseRedirect('/login/')
    else:
        form = UserCreationForm()
    return render(request, 'planning/register.html', {'form': form})

@login_required
def dashboard(request):
    return render(request, 'planning/dashboard.html')

# Workers
def workers(request):
    context = {
        'workers': Workers.objects.all(),
        'workerskills': WorkerSkills.objects.all()
    }
    return render(request, 'planning/workers/workers.html', context)

# Update worker details
class WorkersUpdateView(SuccessMessageMixin, UpdateView):
    model = Workers
    fields = ('name', 'preference', )
    template_name = 'planning/workers/workers_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('workers')
    success_message = "Succesfully edited"

# Delete worker
class WorkersDelete(SuccessMessageMixin, DeleteView):
    model = Workers
    pk_url_kwarg = 'pk'
    template_name = 'planning/workers/workers_delete.html'
    success_url = reverse_lazy('workers')
    success_message = "Succesfully deleted"

# Add new worker
class WorkersCreate(SuccessMessageMixin, CreateView):
    model = Workers
    fields = ('name', )
    template_name = 'planning/workers/workers_add.html'
    success_url = reverse_lazy('workers')
    success_message = "Succesfully created"

# Worker skills page
def workerskills_edit(request, pk):
    unique_skills = WorkerSkills.objects.filter(worker=pk).order_by().values('skill').distinct()
    workerskills = []
    for unique in unique_skills:
        ws = WorkerSkills.objects.filter(worker=pk).filter(skill=unique['skill']).order_by('-date')[0]
        workerskills.append(ws)
    context = {
        'workerskills': workerskills,
        'worker': Workers.objects.get(id=pk)
    }
    return render(request, 'planning/workers/workerskills_edit.html', context)

# Worker skills page
def workerskills_history(request, pk, pk_ws):
    context = {
        'workerskills': WorkerSkills.objects.filter(worker=pk).filter(skill=pk_ws).order_by('-date'),
        'workerskills_up': WorkerSkills.objects.filter(worker=pk).filter(skill=pk_ws).order_by('date'),
        'worker': Workers.objects.get(id=pk)
    }
    return render(request, 'planning/workers/workerskills_history.html', context)


# Add new skills to worker
class WorkerSkillsCreate(SuccessMessageMixin, CreateView):
    model = WorkerSkills
    fields = ('date', 'skill', 'productivity')
    def form_valid(self, form):
        form.instance.worker_id = self.kwargs['pk']
        return super(WorkerSkillsCreate, self).form_valid(form)
    template_name = 'planning/workers/workerskills_add.html'
    success_message = "Succesfully created"
    def get_success_url(self):
        return reverse('workerskills_edit', kwargs={'pk': self.kwargs['pk']})

# Modify skills from worker
class WorkerSkillsModify(SuccessMessageMixin, CreateView):
    model = WorkerSkills
    fields = ('date', 'productivity')
    def form_valid(self, form):
        form.instance.worker_id = self.kwargs['pk']
        form.instance.skill_id = self.kwargs['pk_ws']
        return super(WorkerSkillsModify, self).form_valid(form)
    template_name = 'planning/workers/workerskills_modify.html'
    success_message = "Succesfully modified"
    def get_success_url(self):
        return reverse('workerskills_edit', kwargs={'pk': self.kwargs['pk']})

# Update productivity from skill
class WorkerSkillsUpdateView(SuccessMessageMixin, UpdateView):
    model = WorkerSkills
    fields = ('date','productivity', )
    template_name = 'planning/workers/workerskills_productivity_edit.html'
    pk_url_kwarg = 'pk_ws'
    success_message = "Succesfully edited"
    def get_success_url(self):
        return reverse('workerskills_edit', kwargs={'pk': self.object.worker.id})
        
# Delete skill from user
class WorkerSkillsDelete(SuccessMessageMixin, DeleteView):
    model = WorkerSkills
    pk_url_kwarg = 'pk_ws'
    template_name = 'planning/workers/workerskills_productivity_delete.html'
    success_message = "Succesfully deleted"
    def get_success_url(self):
        return reverse('workerskills_edit', kwargs={'pk': self.object.worker.id})

# Skills overview
def skills(request):
    context = {
        'skills': Skills.objects.all()
    }
    return render(request, 'planning/workers/skills.html', context)

# Update skill details
class SkillsUpdateView(SuccessMessageMixin, UpdateView):
    model = Skills
    fields = ('name', 'workplaces', 'gross_profit', )
    template_name = 'planning/workers/skills_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('skills')
    success_message = "Succesfully edited"

# Delete skill
class SkillsDelete(SuccessMessageMixin, DeleteView):
    model = Skills
    pk_url_kwarg = 'pk'
    template_name = 'planning/workers/skills_delete.html'
    success_url = reverse_lazy('skills')
    success_message = "Succesfully deleted"

# Add new skill
class SkillsCreate(SuccessMessageMixin, CreateView):
    model = Skills
    fields = ('name','workplaces', 'gross_profit', )
    template_name = 'planning/workers/skills_add.html'
    success_url = reverse_lazy('skills')
    success_message = "Succesfully created"

# Projects overview
def projects(request):
    priorities = ["No priority", "Low priority", "Medium priority", "High priority"]
    context = {
        'tasks': Projects.objects.annotate(num_tasks=Count('tasks', filter=Q(tasks__status=0))),
        'priorities': priorities
    }
    return render(request, 'planning/projects/projects.html', context)

# Update project details
class ProjectsUpdateView(SuccessMessageMixin, UpdateView):
    model = Projects
    fields = ('name', 'due_date', 'status', 'priority',)
    template_name = 'planning/projects/projects_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('projects')
    success_message = "Succesfully edited"

# Delete project
class ProjectsDelete(SuccessMessageMixin, DeleteView):
    model = Projects
    pk_url_kwarg = 'pk'
    template_name = 'planning/projects/projects_delete.html'
    success_url = reverse_lazy('projects')
    success_message = "Succesfully deleted"

# Add new project
class ProjectsCreate(SuccessMessageMixin, CreateView):
    model = Projects
    fields = ('name','creation_date','due_date','status','priority',)
    template_name = 'planning/projects/projects_add.html'
    success_url = reverse_lazy('projects')
    success_message = "Succesfully created"

# Project detail
def viewprojects(request, pk):
    priorities = ["No priority", "Low priority", "Medium priority", "High priority"]
    status = ["Open", "Closed"]
    context = {
        'tasks': Tasks.objects.filter(project=pk).order_by('due_date'),
        'project': Projects.objects.get(id=pk),
        'priorities': priorities,
        'status': status
    }
    return render(request, 'planning/projects/projects_details.html', context)

# Add new task to a project
class TasksCreate(SuccessMessageMixin, CreateView):
    model = Tasks
    fields = ('name','due_date','skills','priority','status',)
    def form_valid(self, form):
        form.instance.project_id = self.kwargs['pk']
        return super(TasksCreate, self).form_valid(form)
    template_name = 'planning/projects/tasks_add.html'
    success_message = "Succesfully created"
    def get_success_url(self):
        return reverse('projects_view', kwargs={'pk': self.kwargs['pk']})


# Update task from project
class TasksUpdateView(SuccessMessageMixin, UpdateView):
    model = Tasks
    fields = ('name','due_date','skills','priority','status', )
    template_name = 'planning/projects/tasks_edit.html'
    pk_url_kwarg = 'pk_task'
    success_message = "Succesfully edited"
    def get_success_url(self):
        return reverse('projects_view', kwargs={'pk': self.object.project.id})
        
# Delete task from project
class TasksDelete(SuccessMessageMixin, DeleteView):
    model = Tasks
    pk_url_kwarg = 'pk_task'
    template_name = 'planning/projects/tasks_delete.html'
    success_message = "Succesfully deleted"
    def get_success_url(self):
        return reverse('projects_view', kwargs={'pk': self.object.project.id})

# Shifts overview
def shifts(request):
    context = {
        'shifts': Shifts.objects.all()
    }
    return render(request, 'planning/planning/shifts.html', context)

# Update shift details
class ShiftsUpdateView(SuccessMessageMixin, UpdateView):
    model = Shifts
    fields = ('name', 'length',)
    template_name = 'planning/planning/shifts_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('shifts')
    success_message = "Succesfully edited"

# Delete shift
class ShiftsDelete(SuccessMessageMixin, DeleteView):
    model = Shifts
    pk_url_kwarg = 'pk'
    template_name = 'planning/planning/shifts_delete.html'
    success_url = reverse_lazy('shifts')
    success_message = "Succesfully deleted"

# Add new shift
class ShiftsCreate(SuccessMessageMixin, CreateView):
    model = Shifts
    fields = ('name','length',)
    template_name = 'planning/planning/shifts_add.html'
    success_url = reverse_lazy('shifts')
    success_message = "Succesfully created"

# Availability overview
def availability(request):
    today = datetime.datetime.today()
    sort = request.GET.get('sort')
    if request.method == 'GET' and sort == 'all':
        context = {
            'availabilities': Availability.objects.order_by('-date'),
            'shifts': Shifts.objects.all()
        }
    else:
        context = {
            'availabilities': Availability.objects.filter(Q(date__gte=today)).order_by('-date'),
            'shifts': Shifts.objects.all()
        }

    return render(request, 'planning/planning/availability.html', context)

# Update availability details
class AvailabilityUpdateView(SuccessMessageMixin, UpdateView):
    model = Availability
    fields = ('shift',)
    template_name = 'planning/planning/availability_edit.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('availability')
    success_message = "Succesfully edited"

# Delete availability
class AvailabilityDelete(SuccessMessageMixin, DeleteView):
    model = Availability
    pk_url_kwarg = 'pk'
    template_name = 'planning/planning/availability_delete.html'
    success_url = reverse_lazy('availability')
    success_message = "Succesfully deleted"

# Add new availability
class AvailabilityCreate(SuccessMessageMixin, CreateView):
    model = Availability
    fields = ('worker','date','shift',)
    template_name = 'planning/planning/availability_add.html'
    success_url = reverse_lazy('availability')
    success_message = "Succesfully created"

def planning(request):
    return render(request, 'planning/planning/planning.html')

def planning_create(request):
    form = PlanningForm()
    return render(request, 'planning/planning/planning_create.html', {'form': form})

def planning_result(request):
    if request.method == 'POST':
        form = PlanningForm(request.POST)
        if form.is_valid():
            data = request.POST.copy()
            input_date = data.get('date') # Get the POST date in YYYY-MM-DD value

            # Get the minimum and maximum output per skill
            min_values = {}
            max_values = {}
            for setting in request.POST.dict():
                name = setting[4:]
                if setting.startswith('min_') == True:
                    min_values[name] = float(data.get(setting))
                elif setting.startswith('max_') == True:
                    max_values[name] = float(data.get(setting))

            # Obtain list of available people
            availabilities = Availability.objects.filter(date=input_date)
            model_availabilities = {}
            model_workerskills = {}
            model_preferences = {}
            model_progression = {}
            model_workers = []
            for availability in availabilities:
                model_workers.append(availability.worker.name)
                # Get availability on date
                user_availability = {}
                for shift in Shifts.objects.all():
                    if shift in availability.shift.all():
                        user_availability[shift.name] = 1
                    else:
                        user_availability[shift.name] = 0
                model_availabilities[availability.worker.name] = user_availability
                # Get workerskills of person on the given date and set the preference of the worker
                user_workerskills = {}
                user_preferences = {}
                user_progression = {}
                for skill in Skills.objects.all():
                    if WorkerSkills.objects.filter(worker=availability.worker,skill=skill).exists():
                        user_workerskills[skill.name] = WorkerSkills.objects.filter(Q(date__lte=input_date),worker=availability.worker,skill=skill).values('productivity').order_by('-date')[0]['productivity']
                        # Check if the skill is the preference of the worker, then value 2, 1 otherwise
                        if Workers.objects.filter(pk=availability.worker.id,preference=skill).exists(): 
                            user_preferences[skill.name] = 2
                        else:
                            user_preferences[skill.name] = 1
                    else:
                        user_workerskills[skill.name] = 0
                        user_preferences[skill.name] = 0 # If the worker does not have the skill, it can also not prefer the skill. It must have a starting productivity value.
                    # Determine progression slope
                    x = []
                    y = []
                    observations = WorkerSkills.objects.filter(worker=availability.worker,skill=skill).order_by('date')
                    if observations.count() == 0:
                        # No potential
                        user_progression[skill.name] = 0
                    elif observations.count() == 1:
                        # One observation is unable to determine the potential, hence I set a default.
                        user_progression[skill.name] = 0.5
                    else:
                        i = 0
                        dt = datetime.date(2000, 1, 1) # Set a default datetime
                        for obs in observations:
                            if i == 0:
                                x.append(0)
                                dt = obs.date
                            else:
                                x.append(np.log(float((obs.date - dt).days)))
                            y.append(obs.productivity) 
                            i += 1

                        f = ProgressFit()
                        slope = f.curveFit(x,y)[0]
                        user_progression[skill.name] = (slope / max(x)) if max(x) != 0 else 0.5 # Take the slope of the last (maximum) value of a*ln(x)+b, which is a/x, value is 0.5 if division by zero (i.e., when x = 0)

                model_workerskills[availability.worker.name] = user_workerskills
                model_preferences[availability.worker.name] = user_preferences
                model_progression[availability.worker.name] = user_progression

            # Get maximum workplaces, gross profit per skill and list of skills itself
            model_max_workplaces = {}
            model_gross_profit = {}
            model_skills = []
            for skill in Skills.objects.all():
                model_max_workplaces[skill.name] = skill.workplaces
                model_gross_profit[skill.name] = skill.gross_profit
                model_skills.append(skill.name)
            # Get shift lengths
            model_shift_lengths = {}
            model_shifts = []
            for shift in Shifts.objects.all():
                model_shift_lengths[shift.name] = shift.length
                model_shifts.append(shift.name)

            skills = model_skills
            # Send inputs to solver.py
            function = Optimize()
            max_output = function.maxOutput(model_shifts, model_workers, model_skills, min_values, max_values, model_workerskills, model_availabilities, model_shift_lengths, model_max_workplaces, model_gross_profit, model_preferences, model_progression)
            max_gross_profit = function.maxGrossProfit(model_shifts, model_workers, model_skills, min_values, max_values, model_workerskills, model_availabilities, model_shift_lengths, model_max_workplaces, model_gross_profit, model_preferences, model_progression)
            max_preferences = function.maxPreferences(model_shifts, model_workers, model_skills, min_values, max_values, model_workerskills, model_availabilities, model_shift_lengths, model_max_workplaces, model_gross_profit, model_preferences, model_progression)
            max_progression = function.maxProgression(model_shifts, model_workers, model_skills, min_values, max_values, model_workerskills, model_availabilities, model_shift_lengths, model_max_workplaces, model_gross_profit, model_preferences, model_progression)

            # Radar chart setup
            measure_results = {}
            measures = ['output', 'preference', 'gross_profit', 'skill_progression']
            for measure in measures:
                outputs = [max_output[1][measure], max_preferences[1][measure], max_gross_profit[1][measure], max_progression[1][measure]]
                outputs_perc = []
                for output in outputs:
                    if round(max(outputs)) == 0:
                        outputs_perc.append(0)
                    else:
                        outputs_perc.append(round(output / max(outputs) * 100))
                measure_results[measure] = outputs_perc
            
            pass
            return render(request, 'planning/planning/planning_result.html', {'date': input_date, 'skills': skills, 'max_output': max_output[0], 'max_output_measures': max_output[1], 'max_output_participation': round(max_output[2]*100), 'measures': measure_results, 'max_gross_profit': max_gross_profit[0], 'max_gross_profit_measures': max_gross_profit[1], 'max_gross_profit_participation': round(max_gross_profit[2]*100), 'max_preferences': max_preferences[0], 'max_preferences_measures': max_preferences[1], 'max_preferences_participation': round(max_preferences[2]*100), 'max_progression': max_progression[0], 'max_progression_measures': max_progression[1], 'max_progression_participation': round(max_progression[2]*100)})
    else:
        return redirect('planning_create')