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

| Name                         | Default | Description                                                        |
|:---------------------------- | -------:|:------------------------------------------------------------------ |
| `times_inhours_for_primary`  |       3 | Number of in-hours shifts someone must have done to be a primary.  |
| `times_shadow_for_secondary` |       3 | Number of shadow shifts someone must have done to be a secondary.  |
| `times_oncall_for_secondary` |       3 | Number of on-call shifts someone must have done to be a secondary. |
| `max_times_shadow`           |       3 | Maximum number of times someone can shadow.                        |
| `optimise`                   |  `true` | Whether optimise for the objective functions.                      |


Input format
------------

- `name`: string (must be unique)
- `team`: string (compared stripped and lowercased)
- `can_do_inhours`: bool
- `num_times_inhours`: integer, the number of in-hours non-shadow shifts up to the start of the rota period
- `num_times_shadow`: integer, the number of in-hours shadow shifts up to the start of the rota period
- `can_do_oncall`: bool
- `num_times_oncall`: integer, the number of on-call shifts up to the start of the rota period
- `forbidden_weeks`: integer comma-separated list, weeks unavailable (week 1 = first week of the generated rota)

*Example:*

```csv
name,team,can_do_inhours,num_times_inhours,num_times_shadow,can_do_oncall,num_times_oncall,forbidden_weeks
Oswaldo Bonham,Platform Health,yes,3,2,yes,3,
Jame Truss,Platform Health,yes,3,2,yes,3,
Jarrett Hord,Platform Health ,yes,0,2,no,0,
Neil Hockenberry,Platform Health,yes,3,2,yes,3,
Grant Kornfeld,Platform Health,yes,0,2,no,0,
Bessie Engebretson,Platform Health,yes,3,2,no,0,
Emanuel Leinen,Platform Health ,yes,2,2,no,0,
Sammie Shew,Platform Health,yes,1,2,no,0,
Renae Paton,Platform Health,yes,3,2,no,0,"4,5,6"
Santiago Raine,Platform Health,yes,2,2,no,0,
Chas Stucky,Platform Health,no,0,1,no,0,
Ryan Averett,Publishing Access and Security,yes,3,2,yes,3,
Martin Ashby,FE Dev and Accessibility,yes,3,2,yes,3,"1,3,4,5,6,7,8"
Deloris Baldon,FE Dev and Accessibility,yes,3,2,no,0,
Nyla Drozd,FE Dev and Accessibility,yes,3,2,no,0,"1,2"
Pierre Paulhus,FE Dev and Accessibility,yes,0,0,no,0,
Jerome Silveria,Search,yes,3,2,yes,3,
Wilson Friesen,Structured data,yes,2,2,no,0,
Robin Hoose,Search,yes,2,2,no,0,
Floyd Olsson,Search,yes,3,2,no,0,
Lou Meidinger,Search,yes,3,2,yes,1,"1,2"
Sharleen Woltz,Search,no,0,1,no,0,
Ramon Haddock,Search,no,0,1,no,0,
Jerald Vangundy,Search,yes,2,2,no,0,
Theodore Calvery,Taxonomy,yes,3,2,no,0,
Dewey Burgett,Publisher Workflow,yes,3,2,yes,3,
Irwin Capehart,Publisher Workflow,yes,3,2,no,0,
Jerold Bayes,Publisher Workflow,yes,3,2,yes,3,"5,6,7,12"
Annalisa Harrow,Publisher Workflow,yes,3,2,yes,3,
Dave Allred,Publisher Workflow,yes,3,2,yes,3,
Rocco Morra,Publisher Workflow,yes,3,2,no,0,
Eddie Mccollough,Publisher Workflow,no,0,0,no,0,
Lacy Auyeung,Publisher Workflow,yes,2,2,no,0,
Glynda Laubscher,Publisher Workflow,no,0,1,no,0,"1,8,10,11,12"
Jeannine Demos,Step by step,yes,3,2,yes,3,"1,2"
Vernon Minelli,Step by step,yes,0,1,no,0,
Temeka Lowy,Step by step,yes,0,2,no,0,
Benita Kunz,Step by step,yes,0,2,no,0,
Aubrey Staiger,Personalisation and programme,no,3,2,no,3,
```


Constraints
-----------

1. [Standard rota constraints](rota.md#standard-constraints)
2. In every week:
   1. **Primary** must:
      1. be able to do in-hours support
      2. have been on in-hours support at least `times_inhours_for_primary` times (not including earlier instances in this rota)
   2. **Secondary** must:
      1. be able to do in-hours support
      2. have shadowed at least `times_shadow_for_secondary` times (not including earlier instances in this rota)
   3. **Shadow** must:
      1. be able to do in-hours support
      2. have shadowed at most `max_times_shadow` times before (not including earlier instances in this rota)
   4. **Primary oncall** must be able to do out-of-hours support
   5. **Secondary oncall** must:
      1. be able to do out-of-hours support
      2. have done out-of-hours support at least `times_oncall_for_secondary` times (not including earlier instances in this rota)
3. A person must:
   1. not be assigned roles in two adjacent weeks
   2. not be assigned more than `max-in-hours-shifts` in-hours roles in total
   3. not be assigned more than `max-on-call-shifts` out-of-hours roles in total
   4. not be on in-hours support in the same week that someone else from their team is also on in-hours support
   5. not be on in-hours support in the week after someone else from their team is also on in-hours support


Objectives
----------

1. *Maximise* the number of people with assignments.
2. *Maximise* the number of weeks where **secondary** has been on in-hours support fewer than `times_inhours_for_primary` times.
3. *Maximise* the number of weeks where **primary oncall** has been on out-of-hours support fewer than `times_oncall_for_secondary` times.
4. *Maximise* the number of weeks with a **shadow**.

*Commentary:*

**O1** is a proxy for minimising the maximum number of roles-assignments any one person has.
