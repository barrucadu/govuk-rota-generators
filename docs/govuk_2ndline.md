GOV.UK 2ndline (developer) support rota
=======================================

Generates a weekly rota with these roles:

- **Primary** and **secondary**, in-hours support
- **Shadow** *(optional)*, someone who learns the ropes in-hours
- **Primary oncall** and **secondary oncall**, the out-of-hours support


Parameters
----------

| Flag                        | Default | Description                                         |
|:--------------------------- | -------:|:--------------------------------------------------- |
| `--num-weeks=<n>`           |      12 | Number of weeks to generate.                        |
| `--max-in-hours-shifts=<n>` |       1 | Maximum number of in-hours shifts someone can have. |
| `--max-on-call-shifts=<n>`  |       3 | Maximum number of on-call shifts someone can have.  |

*Internal parameters:*

| Name        | Default | Description                                   |
|:------------| -------:|:--------------------------------------------- |
| `optimise`  |  `true` | Whether optimise for the objective functions. |


Input format
------------

- `name`: string (must be unique)
- `team`: string (compared stripped and lowercased)-
- `can_do_inhours_primary`: bool
- `can_do_inhours_secondary`: bool
- `can_do_inhours_shadow`: bool
- `can_do_oncall_primary`: bool
- `can_do_oncall_secondary`: bool
- `forbidden_weeks`: integer comma-separated list, weeks unavailable (week 1 = first week of the generated rota)

*Example:*

```csv
name,team,can_do_inhours_primary,can_do_inhours_secondary,can_do_inhours_shadow,can_do_oncall_primary,can_do_oncall_secondary,forbidden_weeks
Oswaldo Bonham,Platform Health,yes,yes,no,yes,yes,
Jame Truss,Platform Health,yes,yes,no,yes,yes,
Jarrett Hord,Platform Health,yes,yes,no,no,yes,
Neil Hockenberry,Platform Health,yes,yes,no,yes,yes,
Grant Kornfeld,Platform Health,yes,yes,no,no,yes,
Bessie Engebretson,Platform Health,yes,yes,no,no,no,
Emanuel Leinen,Platform Health ,yes,yes,no,no,no,
Sammie Shew,Platform Health,yes,yes,no,no,yes,
Renae Paton,Platform Health,yes,yes,no,no,yes,"4,5,6"
Santiago Raine,Platform Health,yes,yes,no,no,yes,
Chas Stucky,Platform Health,no,no,yes,no,no,
Ryan Averett,Publishing Access and Security,yes,yes,no,yes,yes,
Martin Ashby,FE Dev and Accessibility,yes,yes,no,yes,yes,"1,3,4,5,6,7,8"
Deloris Baldon,FE Dev and Accessibility,yes,yes,no,no,no,
Nyla Drozd,FE Dev and Accessibility,yes,yes,no,no,no,"1,2"
Pierre Paulhus,FE Dev and Accessibility,yes,yes,no,no,no,
Jerome Silveria,Search,yes,yes,no,yes,yes,
Wilson Friesen,Structured data,yes,yes,no,no,yes,
Robin Hoose,Search,yes,yes,no,no,yes,
Floyd Olsson,Search,yes,yes,no,no,yes,
Lou Meidinger,Search,yes,yes,no,yes,1,"1,2"
Sharleen Woltz,Search,no,0,1,no,0,
Ramon Haddock,Search,no,0,1,no,0,
Jerald Vangundy,Search,yes,yes,no,no,0,
Theodore Calvery,Taxonomy,yes,yes,no,no,0,
Dewey Burgett,Publisher Workflow,yes,yes,no,yes,yes,
Irwin Capehart,Publisher Workflow,yes,yes,no,no,yes,
Jerold Bayes,Publisher Workflow,yes,yes,no,yes,yes,"5,6,7,12"
Annalisa Harrow,Publisher Workflow,yes,yes,no,yes,yes,
Dave Allred,Publisher Workflow,yes,yes,no,yes,yes,
Rocco Morra,Publisher Workflow,yes,yes,no,no,no,
Eddie Mccollough,Publisher Workflow,no,0,0,no,no,
Lacy Auyeung,Publisher Workflow,yes,yes,no,no,yes,
Glynda Laubscher,Publisher Workflow,no,no,yes,no,no,"1,8,10,11,12"
Jeannine Demos,Step by step,yes,yes,no,yes,yes,"1,2"
Vernon Minelli,Step by step,yes,yes,no,no,no,
Temeka Lowy,Step by step,yes,yes,no,no,yes,
Benita Kunz,Step by step,yes,yes,no,no,no,
Aubrey Staiger,Personalisation and programme,no,yes,no,no,no,
```


Constraints
-----------

1. [Standard rota constraints](rota.md#standard-constraints)
2. A person must:
   1. not be assigned a role they can't take
   2. not be assigned roles in two adjacent weeks
   3. not be assigned more than `max-in-hours-shifts` in-hours roles in total
   4. not be assigned more than `max-on-call-shifts` out-of-hours roles in total
   5. not be on in-hours support in the same week that someone else from their team is also on in-hours support
   6. not be on in-hours support in the week after someone else from their team is also on in-hours support
   7. not be assigned more than `max_inhours_standby` in-hours roles in total
   8. not be on in-hours standby support in the same week that someone else from their team is also on in-hours standby support
   9. not be on out-of-hours support in the same week that someone else from their team is also on out-of-hours support


Objectives
----------

1. *Maximise* the number of people with assignments.
2. *Maximise* the number of weeks with a **shadow**.

*Commentary:*

**O1** is a proxy for minimising the maximum number of roles-assignments any one person has.
