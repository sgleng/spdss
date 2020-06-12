from pyomo.environ import *
from pyomo.opt import SolverFactory
from scipy.optimize import curve_fit
import numpy as np
import pyutilib.subprocess.GlobalData
pyutilib.subprocess.GlobalData.DEFINE_SIGNAL_HANDLERS_DEFAULT = False # To make sure it works on Django

class ProgressFit:
	
	def curveFit(self, x, y):
		def model(x,a,b):
			return a * x + b
		x_val = np.array(x)
		y_val = np.array(y)
		fit,fit_b = curve_fit(model, x_val, y_val)

		return fit

class Optimize:
	def maxOutput(self, shifts, workers, skills, min_values, max_values, workerskills, availability, shift_lengths, max_workplaces, gross_profit, preferences, progression):
		"""Description of the function

		Parameters:
		shifts (list): list of the shifts that are available to be planned
		workers (list): list of all workers that are part of the planning
		skills (list): list of all skills
		min_values (dict): dictionary of the minimum required output per skill
		max_values (dict): dictionary of the maximum required output per skill
		workerskills (dict): dictionary of the output per skill per time unit per worker
		availability (dict): dictionary of the availability per timeslot per worker
		shift_lengths (dict): dictionary of the shift length per shift in time unit (mostly hours)
		max_workplaces (dict): dictionary of the maximum of workplaces available per timeslot per skill
		gross_profit (dict): dictionary of the gross profit per output of skill
		preferences (dict): dictionary of the preferences per worker
		progression (dict): dictionary of the progression per worker

		Objective:
		maximize the total output based on the above-stated parameters

		Returns:
		dict:timetable, dict:{output, preference, gross_profit, progression}, int:participation

		"""

		warnings = []
		model = ConcreteModel()
		model.works = Var(((skill, worker, shift) for worker in workers for skill in skills for shift in shifts),
			within=Binary, initialize=0)

		def obj_function(m):
			total = 0
			for skill in skills:
				for shift in shifts:
					total += sum(m.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift]
			return total

		model.obj = Objective(rule=obj_function, sense=maximize)

		model.constraints = ConstraintList()

		# Constraints
		# Max one task per worker per timeslot

		for shift in shifts:
			for worker in workers:
				model.constraints.add(
					1 >= sum(model.works[skill, worker, shift] for skill in skills)
				)

		# Dot not plan when the worker is not available
		for worker, timeslot in availability.items():
			for key in timeslot:
				if timeslot[key] == 0:
					model.constraints.add(
						0 == sum(model.works[skill, worker, key] for skill in skills)
					)

		# Maximum number of workplaces per shift
		for shift in shifts:
			for skill in skills:
				model.constraints.add(
					max_workplaces[skill] >= sum(model.works[skill, worker, shift] for worker in workers)
				)

		# Output per skill cannot be higher than the provided max number
		model.outputSet = Set(initialize=skills)
		def skills_rule(model, skill):
			temp = sum(sum(model.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] for shift in shifts)
			if type(temp) is float: # Not every combination of skills, workers, and shifts, multiplied by workerskills appear in the matrix. Hence, in that case: skip the constraint.
				return Constraint.Skip
			else:
				return temp <= max_values[skill]
		model.sr = Constraint(model.outputSet, rule=skills_rule)

		# Output per skill must be higher than the provided min value
		model.outputMinSet = Set(initialize=skills)
		def skills_min_rule(model, skill):
			temp = sum(sum(model.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] for shift in shifts)
			if type(temp) is float: # Not every combination of skills, workers, and shifts, multiplied by workerskills appear in the matrix. Hence, in that case: skip the constraint.
				return Constraint.Skip
			else:
				return temp >= min_values[skill]
		model.smr = Constraint(model.outputMinSet, rule=skills_min_rule)

		# Solver
		opt = SolverFactory('cbc')  # cbc solver as it is open-source
		results = opt.solve(model)

		# Outputs
		def timetable(works):
		    table = {shift: {skill: [] for skill in skills} for shift in shifts}
		    for worker in workers:
		    	for skill in skills:
		    		for shift in shifts:
		    			if works[skill, worker, shift].value == 1:
		    				table[shift][skill].append(worker)
		    return table

		def participation(works):
			total = 0
			for worker in availability:
				for shift in shifts:
					if availability[worker][shift] == 1:
						total += 1

			deployed = 0
			for worker in workers:
				for skill in skills:
					for shift in shifts:
						if works[skill, worker, shift].value == 1:
							deployed += 1
			return (deployed/total)

		def output(works):
			var = 0
			for skill in skills:
					for shift in shifts:
						var += sum(model.works[skill, worker, shift].value*workerskills[worker][skill] for worker in workers) * shift_lengths[shift]
			return round(var,2)
		
		def preference(works):
			var = 0
			for worker in workers:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*preferences[worker][skill] for skill in skills) * shift_lengths[shift]
			return round(var,2)

		def grossprofit(works):
			var = 0
			for skill in skills:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] * gross_profit[skill]
			return round(var,2)

		def skillprogression(works):
			var = 0
			for worker in workers:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*progression[worker][skill] for skill in skills) * shift_lengths[shift]
			return round(var,2)

		for skill in max_values:
			total = 0
			for shift in shifts:
				for worker in workers:
					total += model.works[skill, worker, shift].value * workerskills[worker][skill] * shift_lengths[shift]
			warnings.append(total)

		return [timetable(model.works), {'output': output(model.works), 'preference': preference(model.works), 'gross_profit': grossprofit(model.works), 'skill_progression': skillprogression(model.works)}, participation(model.works)]

	def maxGrossProfit(self, shifts, workers, skills, min_values, max_values, workerskills, availability, shift_lengths, max_workplaces, gross_profit, preferences, progression):
		"""Description of the function

		Parameters:
		shifts (list): list of the shifts that are available to be planned
		workers (list): list of all workers that are part of the planning
		skills (list): list of all skills
		min_values (dict): dictionary of the minimum required output per skill
		max_values (dict): dictionary of the maximum required output per skill
		workerskills (dict): dictionary of the output per skill per time unit per worker
		availability (dict): dictionary of the availability per timeslot per worker
		shift_lengths (dict): dictionary of the shift length per shift in time unit (mostly hours)
		max_workplaces (dict): dictionary of the maximum of workplaces available per timeslot per skill
		gross_profit (dict): dictionary of the gross profit per output of skill
		preferences (dict): dictionary of the preferences per worker
		progression (dict): dictionary of the progression per worker

		Objective:
		maximize the total gross profit based on the above-stated parameters

		Returns:
		dict:timetable, dict:{output, preference, gross_profit, progression}, int:participation

		"""

		model = ConcreteModel()
		model.works = Var(((skill, worker, shift) for worker in workers for skill in skills for shift in shifts),
			within=Binary, initialize=0)

		def obj_function(m):
			total = 0
			for skill in skills:
				for shift in shifts:
					total += sum(m.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] * gross_profit[skill]
			return total

		model.obj = Objective(rule=obj_function, sense=maximize)

		model.constraints = ConstraintList()

		# Constraints
		# Max one task per worker per timeslot

		for shift in shifts:
			for worker in workers:
				model.constraints.add(
					1 >= sum(model.works[skill, worker, shift] for skill in skills)
				)

		# Dot not plan when the worker is not available
		for worker, timeslot in availability.items():
			for key in timeslot:
				if timeslot[key] == 0:
					model.constraints.add(
						0 == sum(model.works[skill, worker, key] for skill in skills)
					)

		# Maximum number of workplaces per shift
		for shift in shifts:
			for skill in skills:
				model.constraints.add(
					max_workplaces[skill] >= sum(model.works[skill, worker, shift] for worker in workers)
				)

		# Output per skill cannot be higher than the provided max value
		model.outputSet = Set(initialize=skills)
		def skills_rule(model, skill):
			temp = sum(sum(model.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] for shift in shifts)
			if type(temp) is float: # Not every combination of skills, workers, and shifts, multiplied by workerskills appear in the matrix. Hence, in that case: skip the constraint.
				return Constraint.Skip
			else:
				return temp <= max_values[skill]
		model.sr = Constraint(model.outputSet, rule=skills_rule)

		# Output per skill must be higher than the provided min value
		model.outputMinSet = Set(initialize=skills)
		def skills_min_rule(model, skill):
			temp = sum(sum(model.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] for shift in shifts)
			if type(temp) is float: # Not every combination of skills, workers, and shifts, multiplied by workerskills appear in the matrix. Hence, in that case: skip the constraint.
				return Constraint.Skip
			else:
				return temp >= min_values[skill]
		model.smr = Constraint(model.outputMinSet, rule=skills_min_rule)

		# Solver
		opt = SolverFactory('cbc')  # cbc solver as it is open-source
		results = opt.solve(model)

		# Outputs
		def timetable(works):
		    table = {shift: {skill: [] for skill in skills} for shift in shifts}
		    for worker in workers:
		    	for skill in skills:
		    		for shift in shifts:
		    			if works[skill, worker, shift].value == 1:
		    				table[shift][skill].append(worker)
		    return table

		def participation(works):
			total = 0
			for worker in availability:
				for shift in shifts:
					if availability[worker][shift] == 1:
						total += 1

			deployed = 0
			for worker in workers:
				for skill in skills:
					for shift in shifts:
						if works[skill, worker, shift].value == 1:
							deployed += 1
			return (deployed/total)

		def output(works):
			var = 0
			for skill in skills:
					for shift in shifts:
						var += sum(model.works[skill, worker, shift].value*workerskills[worker][skill] for worker in workers) * shift_lengths[shift]
			return round(var,2)
		
		def preference(works):
			var = 0
			for worker in workers:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*preferences[worker][skill] for skill in skills) * shift_lengths[shift]
			return round(var,2)

		def grossprofit(works):
			var = 0
			for skill in skills:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] * gross_profit[skill]
			return round(var,2)

		def skillprogression(works):
			var = 0
			for worker in workers:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*progression[worker][skill] for skill in skills) * shift_lengths[shift]
			return round(var,2)

		return [timetable(model.works), {'output': output(model.works), 'preference': preference(model.works), 'gross_profit': grossprofit(model.works), 'skill_progression': skillprogression(model.works)}, participation(model.works)]

	def maxPreferences(self, shifts, workers, skills, min_values, max_values, workerskills, availability, shift_lengths, max_workplaces, gross_profit, preferences, progression):
		"""Description of the function

		Parameters:
		shifts (list): list of the shifts that are available to be planned
		workers (list): list of all workers that are part of the planning
		skills (list): list of all skills
		min_values (dict): dictionary of the minimum required output per skill
		max_values (dict): dictionary of the maximum required output per skill
		workerskills (dict): dictionary of the output per skill per time unit per worker
		availability (dict): dictionary of the availability per timeslot per worker
		shift_lengths (dict): dictionary of the shift length per shift in time unit (mostly hours)
		max_workplaces (dict): dictionary of the maximum of workplaces available per timeslot per skill
		gross_profit (dict): dictionary of the gross profit per output of skill
		preferences (dict): dictionary of the preferences per worker
		progression (dict): dictionary of the progression per worker

		Objective:
		maximize the preferences of workers based on the above-stated parameters

		Returns:
		dict:timetable, dict:{output, preference, gross_profit, progression}, int:participation

		"""

		model = ConcreteModel()
		model.works = Var(((skill, worker, shift) for worker in workers for skill in skills for shift in shifts),
			within=Binary, initialize=0)

		def obj_function(m):
			total = 0
			for worker in workers:
				for shift in shifts:
					total += sum(m.works[skill, worker, shift]*preferences[worker][skill] for skill in skills) * shift_lengths[shift]
			return total

		model.obj = Objective(rule=obj_function, sense=maximize)

		model.constraints = ConstraintList()

		# Constraints
		# Max one task per worker per timeslot

		for shift in shifts:
			for worker in workers:
				model.constraints.add(
					1 >= sum(model.works[skill, worker, shift] for skill in skills)
				)

		# Dot not plan when the worker is not available
		for worker, timeslot in availability.items():
			for key in timeslot:
				if timeslot[key] == 0:
					model.constraints.add(
						0 == sum(model.works[skill, worker, key] for skill in skills)
					)

		# Maximum number of workplaces per shift
		for shift in shifts:
			for skill in skills:
				model.constraints.add(
					max_workplaces[skill] >= sum(model.works[skill, worker, shift] for worker in workers)
				)

		# Output per skill cannot be higher than the provided max value
		model.outputSet = Set(initialize=skills)
		def skills_rule(model, skill):
			temp = sum(sum(model.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] for shift in shifts)
			if type(temp) is float: # Not every combination of skills, workers, and shifts, multiplied by workerskills appear in the matrix. Hence, in that case: skip the constraint.
				return Constraint.Skip
			else:
				return temp <= max_values[skill]
		model.sr = Constraint(model.outputSet, rule=skills_rule)

		# Output per skill must be higher than the provided min value
		model.outputMinSet = Set(initialize=skills)
		def skills_min_rule(model, skill):
			temp = sum(sum(model.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] for shift in shifts)
			if type(temp) is float: # Not every combination of skills, workers, and shifts, multiplied by workerskills appear in the matrix. Hence, in that case: skip the constraint.
				return Constraint.Skip
			else:
				return temp >= min_values[skill]
		model.smr = Constraint(model.outputMinSet, rule=skills_min_rule)

		# Solver
		opt = SolverFactory('cbc')  # cbc solver as it is open-source
		results = opt.solve(model)

		# Outputs
		def timetable(works):
		    table = {shift: {skill: [] for skill in skills} for shift in shifts}
		    for worker in workers:
		    	for skill in skills:
		    		for shift in shifts:
		    			if works[skill, worker, shift].value == 1:
		    				table[shift][skill].append(worker)
		    return table

		def participation(works):
			total = 0
			for worker in availability:
				for shift in shifts:
					if availability[worker][shift] == 1:
						total += 1

			deployed = 0
			for worker in workers:
				for skill in skills:
					for shift in shifts:
						if works[skill, worker, shift].value == 1:
							deployed += 1
			return (deployed/total)

		def output(works):
			var = 0
			for skill in skills:
					for shift in shifts:
						var += sum(model.works[skill, worker, shift].value*workerskills[worker][skill] for worker in workers) * shift_lengths[shift]
			return round(var,2)
		
		def preference(works):
			var = 0
			for worker in workers:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*preferences[worker][skill] for skill in skills) * shift_lengths[shift]
			return round(var,2)

		def grossprofit(works):
			var = 0
			for skill in skills:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] * gross_profit[skill]
			return round(var,2)

		def skillprogression(works):
			var = 0
			for worker in workers:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*progression[worker][skill] for skill in skills) * shift_lengths[shift]
			return round(var,2)

		return [timetable(model.works), {'output': output(model.works), 'preference': preference(model.works), 'gross_profit': grossprofit(model.works), 'skill_progression': skillprogression(model.works)}, participation(model.works)]

	def maxProgression(self, shifts, workers, skills, min_values, max_values, workerskills, availability, shift_lengths, max_workplaces, gross_profit, preferences, progression):
		"""Description of the function

		Parameters:
		shifts (list): list of the shifts that are available to be planned
		workers (list): list of all workers that are part of the planning
		skills (list): list of all skills
		min_values (dict): dictionary of the minimum required output per skill
		max_values (dict): dictionary of the maximum required output per skill
		workerskills (dict): dictionary of the output per skill per time unit per worker
		availability (dict): dictionary of the availability per timeslot per worker
		shift_lengths (dict): dictionary of the shift length per shift in time unit (mostly hours)
		max_workplaces (dict): dictionary of the maximum of workplaces available per timeslot per skill
		gross_profit (dict): dictionary of the gross profit per output of skill
		preferences (dict): dictionary of the preferences per worker
		progression (dict): dictionary of the progression per worker

		Objective:
		maximize the total progression of workers based on the above-stated parameters

		Returns:
		dict:timetable, dict:{output, preference, gross_profit, progression}, int:participation

		"""

		model = ConcreteModel()
		model.works = Var(((skill, worker, shift) for worker in workers for skill in skills for shift in shifts),
			within=Binary, initialize=0)

		def obj_function(m):
			total = 0
			for worker in workers:
				for shift in shifts:
					total += sum(m.works[skill, worker, shift]*progression[worker][skill] for skill in skills) * shift_lengths[shift]
			return total

		model.obj = Objective(rule=obj_function, sense=maximize)

		model.constraints = ConstraintList()

		# Constraints
		# Max one task per worker per timeslot

		for shift in shifts:
			for worker in workers:
				model.constraints.add(
					1 >= sum(model.works[skill, worker, shift] for skill in skills)
				)

		# Dot not plan when the worker is not available
		for worker, timeslot in availability.items():
			for key in timeslot:
				if timeslot[key] == 0:
					model.constraints.add(
						0 == sum(model.works[skill, worker, key] for skill in skills)
					)

		# Maximum number of workplaces per shift
		for shift in shifts:
			for skill in skills:
				model.constraints.add(
					max_workplaces[skill] >= sum(model.works[skill, worker, shift] for worker in workers)
				)

		# Output per skill cannot be higher than the provided max value
		model.outputSet = Set(initialize=skills)
		def skills_rule(model, skill):
			temp = sum(sum(model.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] for shift in shifts)
			if type(temp) is float: # Not every combination of skills, workers, and shifts, multiplied by workerskills appear in the matrix. Hence, in that case: skip the constraint.
				return Constraint.Skip
			else:
				return temp <= max_values[skill]
		model.sr = Constraint(model.outputSet, rule=skills_rule)

		# Output per skill must be higher than the provided min value
		model.outputMinSet = Set(initialize=skills)
		def skills_min_rule(model, skill):
			temp = sum(sum(model.works[skill, worker, shift]*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] for shift in shifts)
			if type(temp) is float: # Not every combination of skills, workers, and shifts, multiplied by workerskills appear in the matrix. Hence, in that case: skip the constraint.
				return Constraint.Skip
			else:
				return temp >= min_values[skill]
		model.smr = Constraint(model.outputMinSet, rule=skills_min_rule)

		# Solver
		opt = SolverFactory('cbc')  # cbc solver as it is open-source
		results = opt.solve(model)

		# Outputs
		def timetable(works):
		    table = {shift: {skill: [] for skill in skills} for shift in shifts}
		    for worker in workers:
		    	for skill in skills:
		    		for shift in shifts:
		    			if works[skill, worker, shift].value == 1:
		    				table[shift][skill].append(worker)
		    return table

		def participation(works):
			total = 0
			for worker in availability:
				for shift in shifts:
					if availability[worker][shift] == 1:
						total += 1

			deployed = 0
			for worker in workers:
				for skill in skills:
					for shift in shifts:
						if works[skill, worker, shift].value == 1:
							deployed += 1
			return (deployed/total)

		def output(works):
			var = 0
			for skill in skills:
					for shift in shifts:
						var += sum(model.works[skill, worker, shift].value*workerskills[worker][skill] for worker in workers) * shift_lengths[shift]
			return round(var,2)
		
		def preference(works):
			var = 0
			for worker in workers:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*preferences[worker][skill] for skill in skills) * shift_lengths[shift]
			return round(var,2)

		def grossprofit(works):
			var = 0
			for skill in skills:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*workerskills[worker][skill] for worker in workers) * shift_lengths[shift] * gross_profit[skill]
			return round(var,2)

		def skillprogression(works):
			var = 0
			for worker in workers:
				for shift in shifts:
					var += sum(model.works[skill, worker, shift].value*progression[worker][skill] for skill in skills) * shift_lengths[shift]
			return round(var,2)

		return [timetable(model.works), {'output': output(model.works), 'preference': preference(model.works), 'gross_profit': grossprofit(model.works), 'skill_progression': skillprogression(model.works)}, participation(model.works)]