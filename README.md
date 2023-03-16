# `pplan` - Computer-Aided Project Planning

`pplan` is a simple tool to help construct project plans for
work-driven projects, such as those commonly found in software
development. The user inputs a plan consisting of *tasks* and
*resources*, as well as the assignment of resources to tasks, and the
tool will validate the plan for constraint violations and
overallocations, before displaying a summary of task and resource
allocation. In this way, this user can iteratively modify their
assignment of resources to tasks and observe the overall plan
schedule, while being sure that any violations are caught
automatically. The tool has been used successfully to plan software
development projects for small teams (~6 people) over several months.

`pplan` was created out of frustration with Microsoft Project. In
addition to validating constraints and flagging allocation issues,
Project will try to work out the assignment of resources to tasks for
you. Unfortunately, in the author's experience, this often leads to
the software inexplicably being unable to construct assignments which
are logically valid. Additionally, fixing agreeable parts of the
generated schedule yields more constraints which further compounds the
problem. As such, `pplan` was created to remove the automatic
assignment and simply provide the validation. Several limitations were
introduced to simplify the software:

- The core plan is unitless: task work is specified as a positive
  integer without reference to hours, days or weeks. Units can be
  mapped to dates at display time using custom render functions.
- Resource availability is binary for each unit of time, so a resource
  can be assigned to at most one task at any instant.
  
## Usage

`pplan` is implemented as a Python library. See `example.py` for an
example of constructing, validating and printing a plan.

To construct a plan to be validated and displayed, the user will first
specify resources and their availability. Resource availability is
given as a list of boolean values, where all lists are assumed to
start on the same unit. Then, the user will specify the plan's
tasks. Tasks require a unique id, an integer units of work required,
an optional list of constraints and an optional
assignment. Constraints types such as start-to-finish and
finish-to-start are supported, referencing another task id and
optionally specifying a number of units of lag (e.g. constraint type
finish-to-start and a lag of `1` indicates the task cannot start
earlier than one unit after the referenced task ends). The assignment
specifies a set of resources to work on the task at each unit of
time. The task's start and end index are computed as the first and
last non-empty entries in the assignment, and the tool will ensure
these respect any constraints, and that resources are not
overallocated.

The tool first outputs the schedule per task, then the schedule per
resource. Example output:

```
┍━━━━━━━━━━━━━┯━━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━┯━━━━━━━━┯━━━━━━━━━━┯━━━━━━━━┯━━━━━━━━━━┑
│ Task name   │   Start │              │   End │              │ Allocation   │   Allocation (%) │ 02-Jan   │        │ 09-Jan   │        │ 16-Jan   │
┝━━━━━━━━━━━━━┿━━━━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━┿━━━━━━━━━━┿━━━━━━━━┿━━━━━━━━━━┥
│ Development │       0 │ 02-Jan       │     0 │ 02-Jan       │ 1 / 3        │             33.3 │ jsmith   │        │          │        │          │
├─────────────┼─────────┼──────────────┼───────┼──────────────┼──────────────┼──────────────────┼──────────┼────────┼──────────┼────────┼──────────┤
│ Analysis    │       1 │ 02-Jan (1/2) │     3 │ 09-Jan (1/2) │ 2 / 2        │            100   │          │ jsmith │          │ jsmith │          │
┕━━━━━━━━━━━━━┷━━━━━━━━━┷━━━━━━━━━━━━━━┷━━━━━━━┷━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━┷━━━━━━━━┷━━━━━━━━━━┷━━━━━━━━┷━━━━━━━━━━┙
┍━━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━┯━━━━━━━━━━━━━━━━━━┯━━━━━━━━━━┯━━━━━━┯━━━━━━━━━━┯━━━━━━┯━━━━━━━━━━┑
│ Resource id   │ Allocation   │   Allocation (%) │ 02-Jan   │      │ 09-Jan   │      │ 16-Jan   │
┝━━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━┿━━━━━━━━━━━━━━━━━━┿━━━━━━━━━━┿━━━━━━┿━━━━━━━━━━┿━━━━━━┿━━━━━━━━━━┥
│ jsmith        │ 3 / 4        │               75 │ dev      │ alys │ --       │ alys │          │
┕━━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━┷━━━━━━━━━━━━━━━━━━┷━━━━━━━━━━┷━━━━━━┷━━━━━━━━━━┷━━━━━━┷━━━━━━━━━━┙
```

## Miscellaneous

`M-x toggle-truncate-lines` is helpful in the Emacs shell, when
displaying the generated tables for all but the simplest schedules.
