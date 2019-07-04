Content support rota
====================

Generates a daily (in-hours, working days) rota with these roles:

- **2i (A)** and **2i (B)**, 2i rota
- **CR**, content requests
- **2ndline (A)** and **2ndline (B)**, support

Parameters
----------

| Flag              | Default | Description                  |
|:------------------| -------:|:---------------------------- |
| `--num-weeks=<n>` |      12 | Number of weeks to generate. |

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

A bespoke input format is currently being designed.  The current
format is from the data used for the hand-generated rota, so is a bit
strange.

- Each row has four juxtaposed copies of:
  - `name`: string (must be unique)
  - `role`: string (compared stripped and lowercased)
  - `can_do_2ndline`: bool-ish (`y` is true, anything else is false)
  - `can_do_cr`: bool-ish (`y` is true, anything else is false)
  - `can_do_2i`: bool-ish (`y` is true, anything else is false)
  - ignored
  - ignored

The teams are:

- Green
- Red
- Blue
- Product

If a person has no name, they are skipped over as later people in the
same row may be present.

*Example:*

```csv
Rota Skills ,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,Y= Yes,N = No,N* = Next up for training,T = undergoing training,- = Trained but not active,,,Y= Yes,N = No,N* = Next up for training,T = undergoing training,- = Trained but not active,,,Y= Yes,N = No,N* = Next up for training,T = undergoing training,- = Trained but not active,,Y= Yes,N = No,N* = Next up for training,T = undergoing training,- = Trained but not active,
Green team ,,,,,,,Red team,,,,,,,Blue team ,,,,,,,Product and Brexit  teams ,,,,,,
Name,Role ,2nd Line,CR,2i,2i Trainer,Style Council,Person,Role,2nd Line,CR,2i,2i Trainer,Style Council,Person,Role,2nd Line,CR,2i ,2i Trainer,Style Council,Name,Role ,2nd Line,CR,2i,2i Trainer,Style Council
Laila Finn,CPL,-,-,-,N,Y,Calandra Youngberg,CPL,-,-,-,N,Y,Hilaria Rothchild,CPL,-,-,-,N,Y,Ming Knipe,CPL,N,N,N,N,N
Johnathan Musante,SCD,-,Y,Y,N,Y,Adan Mchenry,SCD,-,Y ,Y,Y,Y,Angelia Loesch,SCD,-,-,Y,Y,Y,Derrick Easley,CPL,,,,,Y
Ed Even,SCD,-,Y,Y,N,Y,Luke Smelser,SCD,-,Y,Y,Y,Y,Lavinia Matos,SCD,-,Y,N*,N,Y,Bari Kaplan,SCD,N,N,N,N,Y
Harlan Fifer,SCD,-,Y ,N,N,Y,Kisha Ingram,SCD,-,Y,Y,Y,Y,Eileen Keleher,SCD,-,Y,Y,Y,Y,Palmer Askins ,CPL,N,N,Y,N,Y
Harmony Kennington,SCD,-,Y,Y,Y,Y,David Duke,CD,-,Y,Y,N,Y,Brad Crisler,SCD,-,Y,T,N,Y,Holly Urbain,CPL,,,,,Y
Deloras Hoerner,SCD,-,Y,N*,N,Y,Luvenia Trowell,CD,-,Y,N**,N,Y,Mellie Roquemore,CD,-,Y,Y,Y,Y,Bret Long,SCD,,,,,Y
Rebecca Milton,CD,-,N,N,N,Y,Fe Matson,CD,-,Y,N,N,Y,Cecily Mahoney,CD,-,N*,-,-,-,Harold Tankersley,SCD,N,N,N,N,Y
Leonila Bungard ,CD,-,Y,N**,N,N,Domingo Chae,CD,-,N*,N,N,Y,Kina Blan,CD,-,Y,Y,Y,Y,Josef Casado,SCD,,,,,Y
Angelique Bullard,CD,-,-,-,-,-,Melda Kash ,CD,-,N*,Y,-,-,Fiona Vaughn,CD,N,Y,Y,N,Y,Olivia Shontz,SCD,,,,,Y
Forest Mcarthur ,JCD,Y,N,N,N,Y,Antonetta Schwenk,JCD,Y,N,N,N,Y,Tyrell Puff,CD,-,Y,Y,Y,Y,Florentino Talty,CD,,,,,Y
Teisha Montas,JCD,Y,N,N,N,N,,,,,,,,Leone Vanderslice,JCD,Y,N,N,N,Y,Morris Tugwell,SCD,-,Y ,N,N,Y
Leida Marcelino,Intern,Y,N,N,N,N,,,,,,,,Eufemia Meurer,JCD,Y,N,N,N,Y,Tiffaney Willer,CD,-,Y,Y,N,Y
,,,,,,,,,,,,,,,,,,,,,Oliva Klumpp,CD,-,Y,Y,Y,Y
,,,,,,,,,,,,,,,,,,,,,Jamaal Voll,CD,-,Y,Y,Y,Y
,,,,,,,,,,,,,,,,,,,,,Emerald Danforth,SCD,-,Y,Y,Y,Y
,,,,,,,,,,,,,,,,,,,,,,,,,,,
,,,,,,,,,,,,,,Eufemia Meurer ,JCD,Y,N,N,N,Y,,,,,,,
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
