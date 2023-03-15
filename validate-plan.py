from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Set
from itertools import dropwhile
from tabulate import tabulate
from datetime import date, timedelta

TaskId = str
ResourceId = str

@dataclass
class Constraint:
    constraint_type: str         # TODO: make enum or subclasses
    task_id: TaskId
    lag: int = 0

@dataclass
class Task:
    task_id: TaskId
    name: str
    work: int
    constraints: List[Constraint] = field(default_factory=list)
    assignment: List[Set[ResourceId]] = field(default_factory=list)

    def get_assigned_work(self) -> int:
        return sum([len(resource_ids) for resource_ids in self.assignment])

    def get_duration(self) -> Optional[Tuple[int, int]]:
        assigned = list(enumerate([len(resource_ids) > 0 for resource_ids in self.assignment]))
        dropped = list(dropwhile(lambda tup: not tup[1], assigned))
        if not dropped:
            return None
        start_index = dropped[0][0]

        assigned.reverse()
        end_dropped = list(dropwhile(lambda tup: not tup[1], assigned))
        end_index = end_dropped[0][0]

        return start_index, end_index

@dataclass
class Resource:
    resource_id: ResourceId
    name: str
    availability: List[bool]

@dataclass
class Plan:
    tasks: List[Task]
    resources: List[Resource]

    def __post_init__(self):
        task_max_durations = {len(task.assignment) for task in self.tasks}
        self.max_duration = max(task_max_durations) if task_max_durations else 0

    def get_resource_assignment(self, resource_id) -> List[Set[TaskId]]:
        assignment = [set()] * self.max_duration
        for task in self.tasks:
            for i, resource_ids in enumerate(task.assignment):
                if resource_id in resource_ids:
                    assignment[i] = assignment[i] | {task.task_id}
        return assignment

def validate_plan(plan: Plan) -> bool:
    # Assert distinct task ids
    task_ids = {task.task_id for task in plan.tasks}
    if len(task_ids) != len(plan.tasks):
        print("Duplicate task ids!")
        return False

    # Assert distinct resource ids
    resource_ids = {resource.resource_id for resource in plan.resources}
    if len(resource_ids) != len(plan.resources):
        print("Duplicate resource ids!")
        return False

    # Check resources referenced in assignments are defined
    assignment_resource_ids = {resource_id for task in plan.tasks for resource_ids in task.assignment for resource_id in resource_ids}
    if assignment_resource_ids - resource_ids:
        print("Unknown resources:", assignment_resource_ids - resource_ids)
        return False

    # Assert work positive
    if any([task for task in plan.tasks if task.work <= 0]):
        print("Task with non-positive work")
        return False

    resources_dict = {resource.resource_id: resource for resource in plan.resources}

    for resource in plan.resources:
        assignment = plan.get_resource_assignment(resource.resource_id)
        for i, task_ids in enumerate(assignment):
            availability = int(resource.availability[i]) if i < len(resource.availability) else 0
            if len(task_ids) > availability:
                print(f"Resource overallocated (resource id: {resource.resource_id}, index: {i}, allocated tasks: {task_ids}, available: {bool(availability)})")
                return False

    return True

def validate_constraints(plan: Plan) -> bool:
    durations = {task.task_id: task.get_duration() for task in plan.tasks}
    for task in plan.tasks:
        task_id = task.task_id
        duration = durations[task_id]
        if duration is not None:
            start, finish = duration
            for constraint in task.constraints:
                other_duration = durations[constraint.task_id]
                ctype = constraint.constraint_type
                lag = constraint.lag
                if ctype == 'ss':
                    if other_duration is None or other_duration[0] + lag > start:
                        print(f"Constraint violation (task id: {task_id}, constraint type: {ctype}, other task id: {constraint.task_id}, task start: {start}, other start + lag: {other_duration[0] + lag})")
                        return False
                elif ctype == 'sf':
                    if other_duration is None or other_duration[0] + lag > finish:
                        print(f"Constraint violation (task id: {task_id}, constraint type: {ctype}, other task id: {constraint.task_id}, task finish: {finish}, other start + lag: {other_duration[0] + lag})")
                        return False
                elif ctype == 'fs':
                    if other_duration is None or other_duration[1] + lag > start:
                        print(f"Constraint violation (task id: {task_id}, constraint type: {ctype}, other task id: {constraint.task_id}, task start: {start}, other finish + lag: {other_duration[1] + lag})")
                        return False
                elif ctype == 'ff':
                    if other_duration is None or other_duration[1] + lag > finish:
                        print(f"Constraint violation (task id: {task_id}, constraint type: {ctype}, other task id: {constraint.task_id}, task finish: {finish}, other finish + lag: {other_duration[1] + lag})")
                        return False
                else:
                    print(f'Unknown constraint type \'{ctype}\' (task id: {task.task_id})')
                    return False
    return True

# Pre: plan is valid
def print_plan(plan: Plan, render_index = None):
    if render_index is None:
        render_index = lambda i: i

    task_table = []
    task_table_headers = [
        'Task name',
        'Start',
        'End',
        'Allocation',
        'Allocation (%)',
        *[render_index(i) for i in range(plan.max_duration)]
    ]
    for task in plan.tasks:
        duration = task.get_duration()
        start = duration[0] if duration is not None else None
        end = duration[1] if duration is not None else None
        assignment = [
            ', '.join(resource_ids)
            for resource_ids in task.assignment + (plan.max_duration - len(task.assignment)) * [set()]
        ]
        assigned_work = task.get_assigned_work()
        alloc_pct = 100 * assigned_work / task.work
        task_table.append(
            [
                task.name,
                start,
                end,
                f"{assigned_work} / {task.work}",
                f"{alloc_pct:.1f}",
                *assignment
            ]
        )

    print(
        tabulate(
            sorted(task_table, key=lambda row: row[3]), # Sort by end
            headers=task_table_headers,
            tablefmt="mixed_grid"
        )
    )

    resource_table = []
    resource_table_headers = [
        'Resource id',
        'Allocation',
        'Allocation (%)',
        *[render_index(i) for i in range(plan.max_duration)]
    ]
    for resource in plan.resources:
        assignment = plan.get_resource_assignment(resource.resource_id)
        assigned = sum([1 for task_ids in assignment if task_ids])
        availability = resource.availability + [False] * (plan.max_duration - len(resource.availability))
        available = sum([int(b) for b in availability])
        alloc_pct = 100 * assigned / available
        resource_table.append(
            [
                resource.resource_id,
                f"{assigned} / {available}",
                f"{alloc_pct:.1f}",
                *['--' if not available else ','.join(task_ids) for task_ids, available in zip(assignment, availability)]
            ]
        )

    print(
        tabulate(
            sorted(resource_table, key=lambda row: row[0]), # Sort by id
            headers=resource_table_headers,
            tablefmt="mixed_grid"
        )
    )

plan = Plan(
    tasks=[
        Task(
            "mktdata",
            "Market data ingest and analysis",
            work=2,
            assignment=[
                {},
                {'kdav'},
                {},
                {'kdav'},
                {}
            ]
        ),
        Task(
            "boo",
            "blah",
            work=3,
            assignment=[
                {'kdav'},
                {'kdav'}
            ],
            constraints=[
                Constraint(
                    'fs',
                    'mktdata',
                    lag=-2
                )
            ]
        )
    ],
    resources=[
        Resource(
            'kdav',
            'Kunal Dav',
            [
                True,
                True,
                False,
                True,
                True
            ]
        )
    ]
)

def render_half_weeks(start_date: date, index: int) -> str:
    if index % 2 == 0:
        resolved_date = start_date + timedelta(weeks=index // 2)
        return resolved_date.strftime('%d-%b')
    else:
        return ''

def main():
    if not validate_plan(plan) or not validate_constraints(plan):
        exit(1)
    print_plan(plan)

if __name__ == '__main__':
    main()
