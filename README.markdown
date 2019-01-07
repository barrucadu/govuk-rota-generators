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

Run `demo.py` for an example with 12 weeks:

```
> python3 demo.py
GLPSOL: GLPK LP/MIP Solver, v4.65
Parameter(s) specified in the command line:
 --cpxlp /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/eab106047f6a4665a7004d7301fc8150-pulp.lp
 -o /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/eab106047f6a4665a7004d7301fc8150-pulp.sol
Reading problem data from '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/eab106047f6a4665a7004d7301fc8150-pulp.lp'...
11403 rows, 4788 columns, 50415 non-zeros
4788 integer variables, 3492 of which are binary
54164 lines were read
GLPK Integer Optimizer, v4.65
11403 rows, 4788 columns, 50415 non-zeros
4788 integer variables, 3492 of which are binary
Preprocessing...
393 hidden packing inequaliti(es) were detected
807 constraint coefficient(s) were reduced
5244 rows, 2313 columns, 24741 non-zeros
2313 integer variables, 1740 of which are binary
Scaling...
 A: min|aij| =  1.000e+00  max|aij| =  4.500e+01  ratio =  4.500e+01
GM: min|aij| =  4.617e-01  max|aij| =  2.166e+00  ratio =  4.690e+00
EQ: min|aij| =  2.132e-01  max|aij| =  1.000e+00  ratio =  4.690e+00
2N: min|aij| =  2.500e-01  max|aij| =  1.625e+00  ratio =  6.500e+00
Constructing initial basis...
Size of triangular part is 5052
Solving LP relaxation...
GLPK Simplex Optimizer, v4.65
5244 rows, 2313 columns, 24741 non-zeros
      0: obj =  -0.000000000e+00 inf =   6.390e+02 (424)
    582: obj =   1.110264922e+04 inf =   4.719e-13 (0) 2
*   896: obj =   3.603300000e+04 inf =   5.121e-14 (0) 3
OPTIMAL LP SOLUTION FOUND
Integer optimization begins...
Long-step dual simplex will be used
+   896: mip =     not found yet <=              +inf        (1; 0)
+  1607: >>>>>   3.603300000e+04 <=   3.603300000e+04   0.0% (56; 0)
+  1607: mip =   3.603300000e+04 <=     tree is empty   0.0% (0; 111)
INTEGER OPTIMAL SOLUTION FOUND
Time used:   3.2 secs
Memory used: 11.7 Mb (12244084 bytes)
Writing MIP solution to '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/eab106047f6a4665a7004d7301fc8150-pulp.sol'...

== Week 1:
PRIMARY: Helen Jarrard Person(team='D', can_do_inhours=True, num_times_inhours=7, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY: Raye Slone Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[6])
SHADOW: Brant Paskett Person(team='E', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[9])
PRIMARY_ONCALL: Hector Beckett Person(team='D', can_do_inhours=True, num_times_inhours=21, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Gussie Fridley Person(team='A', can_do_inhours=True, num_times_inhours=13, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[1, 7])

== Week 2:
PRIMARY: Lynn Steinhauer Person(team='C', can_do_inhours=True, num_times_inhours=24, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[2])
SECONDARY: Werner Rosenblatt Person(team='E', can_do_inhours=True, num_times_inhours=1, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[3, 10])
PRIMARY_ONCALL: Delisa Polson Person(team='F', can_do_inhours=True, num_times_inhours=15, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[2, 9])
SECONDARY_ONCALL: David Reifsteck Person(team='E', can_do_inhours=True, num_times_inhours=16, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[0, 6])

== Week 3:
PRIMARY: Don Mong Person(team='C', can_do_inhours=True, num_times_inhours=23, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[9])
SECONDARY: Camille Whitmarsh Person(team='A', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[1])
SHADOW: Allyson Mirando Person(team='E', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Eleni Brandy Person(team='C', can_do_inhours=True, num_times_inhours=3, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[0])
SECONDARY_ONCALL: Hector Beckett Person(team='D', can_do_inhours=True, num_times_inhours=21, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])

== Week 4:
PRIMARY: Lucile Spanbauer Person(team='E', can_do_inhours=True, num_times_inhours=14, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[7, 11])
SECONDARY: Isaura Lafuente Person(team='C', can_do_inhours=True, num_times_inhours=1, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[4])
SHADOW: Arlette Mckeighan Person(team='D', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Helen Jarrard Person(team='D', can_do_inhours=True, num_times_inhours=7, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Gussie Fridley Person(team='A', can_do_inhours=True, num_times_inhours=13, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[1, 7])

== Week 5:
PRIMARY: Santiago Mizer Person(team='E', can_do_inhours=True, num_times_inhours=18, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[0, 7])
SECONDARY: Danielle Bence Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[3, 2])
PRIMARY_ONCALL: Delisa Polson Person(team='F', can_do_inhours=True, num_times_inhours=15, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[2, 9])
SECONDARY_ONCALL: Don Mong Person(team='C', can_do_inhours=True, num_times_inhours=23, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[9])

== Week 6:
PRIMARY: David Reifsteck Person(team='E', can_do_inhours=True, num_times_inhours=16, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[0, 6])
SECONDARY: Raye Slone Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[6])
SHADOW: Arlette Mckeighan Person(team='D', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Helen Jarrard Person(team='D', can_do_inhours=True, num_times_inhours=7, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Galen Takemoto Person(team='B', can_do_inhours=True, num_times_inhours=6, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 7:
PRIMARY: Lucile Spanbauer Person(team='E', can_do_inhours=True, num_times_inhours=14, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[7, 11])
SECONDARY: Breana Mar Person(team='B', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[9])
SHADOW: Camille Whitmarsh Person(team='A', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[1])
PRIMARY_ONCALL: Danielle Bence Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[3, 2])
SECONDARY_ONCALL: Delisa Polson Person(team='F', can_do_inhours=True, num_times_inhours=15, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[2, 9])

== Week 8:
PRIMARY: Galen Takemoto Person(team='B', can_do_inhours=True, num_times_inhours=6, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
SECONDARY: Allyson Mirando Person(team='E', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SHADOW: Buffy Nowacki Person(team='F', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[5])
PRIMARY_ONCALL: Eleni Brandy Person(team='C', can_do_inhours=True, num_times_inhours=3, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[0])
SECONDARY_ONCALL: Helen Jarrard Person(team='D', can_do_inhours=True, num_times_inhours=7, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])

== Week 9:
PRIMARY: Kristen Youngren Person(team='D', can_do_inhours=True, num_times_inhours=3, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[9, 0])
SECONDARY: Danielle Bence Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[3, 2])
PRIMARY_ONCALL: Gussie Fridley Person(team='A', can_do_inhours=True, num_times_inhours=13, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[1, 7])
SECONDARY_ONCALL: Don Mong Person(team='C', can_do_inhours=True, num_times_inhours=23, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[9])

== Week 10:
PRIMARY: Helen Jarrard Person(team='D', can_do_inhours=True, num_times_inhours=7, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY: Werner Rosenblatt Person(team='E', can_do_inhours=True, num_times_inhours=1, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[3, 10])
SHADOW: Buffy Nowacki Person(team='F', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[5])
PRIMARY_ONCALL: Eleni Brandy Person(team='C', can_do_inhours=True, num_times_inhours=3, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[0])
SECONDARY_ONCALL: David Reifsteck Person(team='E', can_do_inhours=True, num_times_inhours=16, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[0, 6])

== Week 11:
PRIMARY: Gussie Fridley Person(team='A', can_do_inhours=True, num_times_inhours=13, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[1, 7])
SECONDARY: Isaura Lafuente Person(team='C', can_do_inhours=True, num_times_inhours=1, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[4])
SHADOW: Brant Paskett Person(team='E', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[9])
PRIMARY_ONCALL: Danielle Bence Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[3, 2])
SECONDARY_ONCALL: Galen Takemoto Person(team='B', can_do_inhours=True, num_times_inhours=6, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 12:
PRIMARY: Delisa Polson Person(team='F', can_do_inhours=True, num_times_inhours=15, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[2, 9])
SECONDARY: Breana Mar Person(team='B', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[9])
SHADOW: Elvira Stefani Person(team='D', can_do_inhours=True, num_times_inhours=7, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
PRIMARY_ONCALL: Hector Beckett Person(team='D', can_do_inhours=True, num_times_inhours=21, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: David Reifsteck Person(team='E', can_do_inhours=True, num_times_inhours=16, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[0, 6])
```
