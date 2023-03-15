from datetime import date
from pplan import validate, print_plan, Plan, Constraint, ConstraintType, Task, Resource, render_half_weeks

start_date = date(2023, 1, 2)

plan = Plan(
    tasks=[
        Task(
            "alys",
            "Analysis",
            work=2,
            assignment=[
                {},
                {'jsmith'},
                {},
                {'jsmith'},
                {}
            ]
        ),
        Task(
            "dev",
            "Development",
            work=3,
            assignment=[
                {'jsmith'}
            ],
            constraints=[
                Constraint(
                    ConstraintType.FS,
                    'alys',
                    lag=-3      # Start up to 3 units before end
                )
            ]
        )
    ],
    resources=[
        Resource(
            'jsmith',
            'Jane Smith',
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

def main():
    if not validate(plan):
        exit(1)
    print_plan(
        plan,
        lambda i: render_half_weeks(start_date, i),
        lambda i: render_half_weeks(start_date, i, show_half_weeks=True)
    )

if __name__ == '__main__':
    main()
