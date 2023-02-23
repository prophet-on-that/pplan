from dataclasses import dataclass, field
from typing import List

TaskId = str
ResourceId = str

@dataclass
class Constraint:
    constraintType: str         # TODO: make enum
    taskId: TaskId
    lag: int

@dataclass
class Task:
    task_id: TaskId
    name: str
    work: int
    contraints: List[Constraint] = field(default_factory=list)

@dataclass
class Resource:
    resource_id: ResourceId
    name: str
    availability: List[bool]

@dataclass
class Assignment:
    task_id: str
    assignments: List[List[ResourceId]]

@dataclass
class Plan:
    tasks: List[Task]
    resources: List[Resource]
    assignments: List[Assignment]

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

    # Check tasks referenced in assignments are defined
    assignment_task_ids = {assignment.task_id for assignment in plan.assignments}
    if assignment_task_ids != task_ids:
        print("Unknown tasks:", assignment_task_ids - task_ids)
        return False
    
    # Check resources referenced in assignments are defined
    assignment_resource_ids = {resource_id for assignment in plan.assignments for resource_ids in assignment.assignments for resource_id in resource_ids}
    if assignment_resource_ids != resource_ids:
        print("Unknown resources:", assignment_resource_ids - resource_ids)
        return False

    # Assert work positive
    if any([task for task in plan.tasks if task.work <= 0]):
        print("Task with non-positive work")
        return False

    return True

plan = Plan(
    tasks=[
        Task(
            "mktdata",
            "Market data ingest and analysis",
            2
        )
    ],
    resources=[],
    assignments=[
        Assignment(
            'blah',
            [
                ['kdav']
            ]
        )
    ]
)

def main():
    if not validate_plan(plan):
        exit(1)

if __name__ == '__main__':
    main()
