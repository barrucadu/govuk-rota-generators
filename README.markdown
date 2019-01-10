govuk-2ndline-rota-generator
============================

It does what it says on the tin.

More specifically, generates a support rota for `n` weeks.  The rota
for one week consists of five or six people, assigned to the following
roles:

- **Primary** and **secondary**, in-hours support
- **Shadow** *(optional)*, someone who learns the ropes in-hours
- **Primary oncall** and **secondary oncall**, the out-of-hours support
- **Escalation**, someone from the programme team

Subject to these constraints:

1. In every week:
   1. Each role must be assigned to exactly one person, except **shadow** and **escalation** which may be unassigned.
   2. **Primary** must:
      1. be able to do in-hours support
      2. have been on in-hours support at least 3 times (including earlier instances in this rota)
      3. be at least as experienced as **secondary**
   3. **Secondary** must:
      1. be able to do in-hours support
      2. have shadowed at least twice (including earlier instances in this rota)
   4. **Shadow** must:
      1. be able to do in-hours support
      2. have shadowed at most once before (including earlier instances in this rota)
   5. **Primary oncall** must:
      1. be able to do out-of-hours support
   6. **Secondary oncall** must:
      1. be able to do out-of-hours support
      2. have done out-of-hours support at least 3 times (including earlier instances in this rota)
      3. be at least as experienced as **primary**
  7. **Escalation** must be able to do escalations
2. A person must:
   1. not be assigned more than one role in the same week
   2. not be assigned roles in two adjacent weeks
   3. not be assigned a role in a week they cannot do
   4. not be assigned more than `Ri` in-hours roles in total
   5. not be assigned more than `Ro` out-of-hours roles in total
   6. not be assigned more than `Re` escalation roles in total
   7. not be on in-hours support in the same week that someone else from their team is also on in-hours support
   8. not be on in-hours support in the same week after someone else from their team is also on in-hours support

There's an asymmetry: the **primary** is required to be more
experienced than the **secondary**, but the opposite is the case for
on-call roles.  This is intentional!  If the **primary oncall** were
more experienced, they would resolve every issue themselves and the
less experienced one would never get to learn anything.

If there are multiple rotas which meet the constraints, then ties are
broken by optimisation:

1. *Minimise* the maximum number of roles-assignments any one person has.
2. *Maximise* the number of weeks where **secondary** has been on in-hours support fewer than 3 times
3. *Maximise* the number of weeks where **primary oncall** has been on out-of-hours support fewer than 3 times
4. *Maximise* the number of weeks with a **shadow**

If there are multiple equally good rotas which meet the constraints,
then ties are broken arbitrarily.

## Dependencies

You need [GLPK][], the GNU Linear Programming Kit, installed and in
your `$PATH`.

[GLPK]: https://www.gnu.org/software/glpk/

## Mathematical background

This uses an approach called [integer linear programming][] (ILP), via
the [PuLP library][].  A reasonable introduction to ILP for solving
scheduling problems like this is [the PyCon conference-scheduler
docs][].

[integer linear programming]: https://en.wikipedia.org/wiki/Integer_programming
[PuLP library]: https://pythonhosted.org/PuLP/
[the PyCon conference-scheduler docs]: https://conference-scheduler.readthedocs.io/en/latest/background/mathematical_model.html

## Demo

There is a sample data file, `static/demo.csv`:

```
> ./cli.py static/demo.csv
week,primary,secondary,shadow,primary_oncall,secondary_oncall,escalation
1,Santiago Mizer,Eleni Brandy,Camille Whitmarsh,Elvira Stefani,Galen Takemoto,Natalia Fordham
2,Isaura Lafuente,Randell Gingras,Brant Paskett,Don Mong,Danielle Bence,Oren Bouska
3,Eura Joseph,Hector Beckett,,Delisa Polson,David Reifsteck,Natalia Fordham
4,Jessie Ahlquist,Lucile Spanbauer,,Eleni Brandy,Helen Jarrard,Carolyne Pflug
5,Theodore Hagberg,Gussie Fridley,,Delisa Polson,Galen Takemoto,Clinton Istre
6,Wilfredo Yoshida,Kristyn Wolverton,Allyson Mirando,Elvira Stefani,Eura Joseph,Oren Bouska
7,Werner Rosenblatt,Lynn Steinhauer,Arlette Mckeighan,Eleni Brandy,Hector Beckett,Carolyne Pflug
8,Raye Slone,Katerine Greenwood,,Elvira Stefani,Eura Joseph,Natalia Fordham
9,Mauro Au,Reynalda Botelho,Buffy Nowacki,Eleni Brandy,Galen Takemoto,Oren Bouska
10,Helen Jarrard,Sergio Mcdevitt,Breana Mar,Don Mong,Hector Beckett,Clarita Caiazzo
11,Leticia Grable,Elvira Stefani,,Delisa Polson,Gussie Fridley,Clinton Istre
12,Kristen Youngren,Verda Streit,Galen Takemoto,Don Mong,Hector Beckett,Carolyne Pflug
```

## Running on Heroku

To run this you need the `heroku/python` and `heroku-community/apt`
buildpacks.

The apt buildpack doesn't install shared libraries to the usual
places, so you also need to set `LD_LIBRARY_PATH` to
`/app/.apt/usr/lib/x86_64-linux-gnu/lapack:/app/.apt/usr/lib/x86_64-linux-gnu/blas:/app/.apt/usr/lib/x86_64-linux-gnu`
in your config vars.
