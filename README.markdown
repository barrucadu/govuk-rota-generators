govuk-2ndline-rota-generator
============================

It does what it says on the tin.

More specifically, generates a support rota for `n` weeks.  The rota
for one week consists of four or five people, assigned to the
following roles:

- **Primary** and **secondary**, in-hours support
- **Shadow** *(optional)*, someone who learns the ropes in-hours
- **Primary oncall** and **secondary oncall**, the out-of-hours support

Subject to these constraints:

1. In every week:
   1. Each role must be assigned to exactly one person, except **shadow** which may be unassigned.
   2. **Primary** must:
      1. be able to do in-hours support
      2. have been on in-hours support at least 3 times (including earlier instances in this rota)
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
2. A person must:
   1. not be assigned more than one role in the same week
   2. not be assigned roles in two adjacent weeks
   3. not be assigned a role in a week they cannot do
   4. not be assigned more than `Ri` in-hours roles in total
   5. not be assigned more than `Ro` out-of-hours roles in total
   6. not be on in-hours support in the same week that someone else from their team is also on in-hours support

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

You need [Cbc][] (**C**oin-or **b**ranch and **c**ut) installed and in
your `$PATH`.

[Cbc]: https://projects.coin-or.org/Cbc

## Mathematical background

This uses an approach called [integer linear programming][] (ILP), via
the [PuLP library][].  A reasonable introduction to ILP for solving
scheduling problems like this is [the PyCon conference-scheduler
docs][].

[integer linear programming]: https://en.wikipedia.org/wiki/Integer_programming
[PuLP library]: https://pythonhosted.org/PuLP/
[the PyCon conference-scheduler docs]: https://conference-scheduler.readthedocs.io/en/latest/background/mathematical_model.html

## Demo

There is a sample data file, `demo.csv`:

```
> ./cli.py demo.csv
week,primary,secondary,shadow,primary_oncall,secondary_oncall
1,Hector Beckett,Danielle Bence,Brant Paskett,Eleni Brandy,Galen Takemoto
2,Werner Rosenblatt,Randell Gingras,,Don Mong,David Reifsteck
3,Lucile Spanbauer,Gussie Fridley,,Elvira Stefani,Danielle Bence
4,Don Mong,Verda Streit,,Eleni Brandy,Eura Joseph
5,Mauro Au,Galen Takemoto,,Delisa Polson,Hector Beckett
6,Wilfredo Yoshida,Lynn Steinhauer,Buffy Nowacki,Elvira Stefani,Danielle Bence
7,Raye Slone,David Reifsteck,Camille Whitmarsh,Eleni Brandy,Helen Jarrard
8,Kristyn Wolverton,Nathanael Mejia,Arlette Mckeighan,Delisa Polson,Gussie Fridley
9,Isaura Lafuente,Katerine Greenwood,,Don Mong,Galen Takemoto
10,Santiago Mizer,Reynalda Botelho,Allyson Mirando,Delisa Polson,Danielle Bence
11,Jessie Ahlquist,Helen Jarrard,Breana Mar,Don Mong,Galen Takemoto
12,Leticia Grable,Theodore Hagberg,Sergio Mcdevitt,Elvira Stefani,David Reifsteck
```
