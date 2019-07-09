Content support rota
====================

Generates a daily (in-hours, working days) rota with these roles:

- **2i (A)** and **2i (B)**, 2i rota
- **CR**, content requests
- **2ndline (A)** and **2ndline (B)**, support

Parameters
----------

| Flag                | Default | Description                                        |
|:------------------- | -------:|:-------------------------------------------------- |
| `--num-weeks=<n>`   |      12 | Number of weeks to generate.                       |
| `--leave-start=<n>` |       1 | First period for the leave/unavailability columns. |

*Internal parameters:*

| Name                        | Default | Description                                                   |
|:--------------------------- | -------:|:------------------------------------------------------------- |
| `soft_scd_period_limit`     |       5 | Initial soft limit for gaps between assignments for SCDs.     |
| `soft_other_period_limit`   |       9 | Initial soft limit for gaps between assignments for non-SCDs. |
| `soft_product_people_limit` |       0 | Initial soft limit for number of product people included.     |
| `optimise`                  |  `true` | Whether to perform optimisations.                             |
| `num_cores`                 |       4 | Number of cores to use for solving soft constraints.          |


Input format
------------

- `team`: string in the form "`$name` team" (first word taken)
- `name`: string (must be unique)
- `role`: string (compared stripped and lowercased)
- `can_do_2ndline`: bool
- `can_do_cr`: bool
- `can_do_2i`: bool
- ignored
- ignored

The rest of the row is *unavailability* in the corresponding periods,
with any nonempty (stripped) string meaning that the person is
unavailable.

The teams are:

- Green
- Red
- Blue
- Product

*Example:*

```
Rota Skills ,,,,,,Next = Next up for training,- = Trained but not active,Rota availability,,,Out = can't be on rota for any reason on this day,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri,Mon,Tue,Wed,Thu,Fri
Team,Name,Role ,2nd Line,CR,2i,2i Trainer,Style Council,8 Jan ,9 Jan ,10 Jan ,11 Jan ,12 Jan ,15 Jan ,16 Jan ,17 Jan ,18 Jan ,19 Jan ,22 Jan ,23 Jan ,24 Jan ,25 Jan ,26 Jan ,29 Jan ,30 Jan ,31 Jan ,1 Aug ,2 Aug ,5 Aug ,6 Aug ,7 Aug ,8 Aug ,9 Aug ,12 Aug ,13 Aug ,14 Aug ,15 Aug ,16 Aug ,19 Aug ,20 Aug ,21 Aug ,22 Aug ,23 Aug ,26 Aug ,27 Aug ,28 Aug ,29 Aug ,30 Aug ,2 Sep ,3 Sep ,4 Sep ,5 Sep ,6 Sep ,9 Sep ,10 Sep ,11 Sep ,12 Sep ,13 Sep ,16 Sep ,17 Sep ,18 Sep ,19 Sep ,20 Sep ,23 Sep ,24 Sep ,25 Sep ,26 Sep ,27 Sep ,30 Sep ,1 Oct ,2 Oct ,3 Oct ,4 Oct
Blue team,Ahmad Galasso,CD,Inactive,Yes,Yes,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,April Milligan,CD,Inactive,Yes,Yes,Yes,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Ardella Mundy,SCD,Inactive,Inactive,Yes,Yes,Yes,,Out,,,Out,,,,,Out,,,,,Out,,,,,Out,,,,,Out,,,,,Out,Out,Out,Out,Out,Out,,,,,Out,,,,,Out,,,,,Out,,,,,Out,,,,,Out,,,,,Out
Blue team,Aretha Rittenhouse,JCD,Yes,No,No,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Arthur Musgrave,CD,Inactive,Yes,Yes,No,Yes,,,,,,,,,,,,,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Brittany Potvin,CPL,Inactive,Inactive,Inactive,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Carson Crane,CD,Inactive,Yes,Yes,Yes,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Chastity Brenner,CPL,No,No,No,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Cherie Oney,SCD,Inactive,Yes,Next,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Claud Koger,SCD,No,No,No,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Concha Jines,SCD,Inactive,Inactive,Inactive,Inactive,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Blue team,Dallas Shofner,SCD,Inactive,Yes ,No,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Edmund Mikus,JCD,Yes,No,No,No,Yes,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Elenore Keogh,CD,Inactive,Yes,Yes,Yes,Yes,,Out,,,,,,,,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Ericka Taunton,SCD,Inactive,Yes,Yes,Yes,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Ernie Cloutier,SCD,Inactive,Yes,Yes,No,Yes,,,,,Out,,,,,Out,,,,,,,,,,Out,,,,,Out,,,,,,Out,Out,Out,Out,Out,,Out,Out,Out,Out,,,,,Out,,,,,Out,,,,,,,,,,,,,,,
Green team,Eugenia Gottschalk,SCD,Inactive,Yes,Next,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Freddy Cowen,SCD,Inactive,Yes,In training,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Glenn Godlewski,CPL,Inactive,Inactive,Inactive,No,Yes,,,,,Out,,,,,Out,Out,Out,,,Out,,,,,Out,,,,,Out,,,,,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,,,Out,,,,,Out,,,,,Out,,,,,Out,,,,,Out
Green team,Gloria Raybon,SCD,Inactive,Yes,Yes,Yes,Yes,,,,,Out,,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Jamee Rhone,CD,Inactive,No,No,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Janine Fulbright,CPL,No,No,Yes,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Green team,Janine Hayter,CPL,Inactive,Inactive,Inactive,No,Yes,,,,,,Out,Out,Out,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,,,,,,,,,,,,,,,
Green team,Jason Steele,CPL,Inactive,Inactive,Inactive,Inactive,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Red team,Jerrica Landsman,CD,Inactive,No,No,No,No,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Red team,Johnnie Parmentier,SCD,Inactive,Yes ,Yes,Yes,Yes,,,,,,,,,,,,,,Out,Out,Out,Out,Out,Out,Out,,,,,,,,,,,,,,,,,,,,,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,,,,,,,,,,,,,,,
Red team,Kizzy Wegner,JCD,Yes,No,No,No,Yes,,,,,,,,,,,,,,Out,Out,Out,Out,,,,,,,Out,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Red team,Kristy Faye,CD,Inactive,Yes,No,No,Yes,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Red team,Luana Ybarbo,JCD,Yes,No,No,No,Yes,,,,,,,,,,,,,,,Out,,,,,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Red team,Mallie Trojacek,Intern,Yes,No,No,No,No,,,,,Out,,,,,Out,Out,,,,Out,Out,,,,Out,Out,,,,Out,,,Out,,Out,Out,Out,Out,Out,Out,Out,Out,,,Out,,,Out,,Out,,,Out,,Out,,,Out,,Out,,,Out,,Out,,,Out,,Out
Red team,Mickey Heffley,CD,Inactive,Next,No,No,Yes,,,,,,,,,,,,,,,,,,Out,Out,,,,,,,,,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Red team,Peggie Ellender,CD,Inactive,Yes,Next*,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Red team,Rafaela Shore,CPL,Inactive,Inactive,Inactive,Inactive,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Red team,Raylene Arce,SCD,Inactive,Yes,Yes,Yes,Yes,Out,Out,,,,,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,Out,Out,Out,Out,Out,,,,,,,,,,,,,,,,,,,,
Product teams,Reinaldo Mackley,SCD,Inactive,Yes ,No,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Rosalyn Cadiz,CD,Inactive,Yes,Next*,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Out,,,Out,Out,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Rosanna Kolar,SCD,Inactive,Yes,Yes,No,Yes,,,,,,,,,,,,,,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,,,,,,Out,,,,,,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Roy Bonacci,CD,Inactive,Yes,Yes,Yes,Yes,,,,,,,,,,,,,,,Out,Out,Out,Out,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Sherie Armstead,CD,Inactive,Next,Inactive,Inactive,Inactive,,,Out,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,,,,,,,,,
Product teams,Soo Gines,SCD,Inactive,Inactive,Inactive,Inactive,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Susan Bibby,CD,Inactive,Yes,Yes,Yes,Yes,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,Out,Out,Out,Out,Out,,,,,,,,,,,,Out,Out,Out,Out,,,,,,,,,,,,,,,
Product teams,Takisha Dingus,JCD,Yes,No,No,No,Yes,,,,,Out,Out,Out,Out,Out,Out,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Out,Out,Out,Out,Out,,,,,
Product teams,Thomas Covenant,CD,Inactive,Inactive,Inactive,Inactive,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Tisha Worm,SCD,Inactive,Yes,Yes,Yes,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Titus Forst,SCD,Inactive,Inactive,Inactive,Inactive,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Trista Willems,SCD,No,No,No,No,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Tula Ashlock,CD,Inactive,Next,Yes,Inactive,Inactive,,,,,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,,,,,,,,,,Out,Out,Out,Out,Out,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
Product teams,Velia Emory,SCD,Inactive,Yes,Yes,Yes,Yes,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,,,,,,,,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out,Out
Product teams,Virgil Harling,SCD,Inactive,Yes,Yes,Yes,Yes,,,,,,,,,Out,Out,,,,,Out,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
```


Hard constraints
----------------

1. [Standard rota hard constraints](rota.md#standard-constraints)
2. In every week:
   1. **2i (A)** must be able to do 2i
   2. **2i (B)** must be able to do 2i
   3. **CR** must be able to do CR
   4. **2ndline (A)** must be able to do 2ndline
   5. **2ndline (B)** must be able to do 2ndline
   6. **2i (A)** must be on a different team to **2i (B)**
3. A person must:
   1. not be assigned multiple roles in any 10-day period if they are on a product team
   2. not be assigned roles on adjacent days


Soft constraints
----------------

1. An SCD can only be assigned a 2i or CR role once every 5 days

    *Relaxation:* decrement the number of days, down to 1

2. A non_SCD can only be assigned a 2i or CR role once every 9 days

    *Relaxation:* decrement the number of days, down to 1

3. Only 1 person on a product team can be assigned a role

    *Relaxation:* increment the number of product people, up to the total


Objectives
----------

1. *Maximise* the number of people with assignments.

*Commentary:*

**O1** is a proxy for minimising the maximum number of roles-assignments any one person has.

*To figure out:*

- Optimise for **2ndline (A)** and **2ndline (B)** being on different teams
- Optimise for part-time people being included less than full-time people (but not being excluded)
