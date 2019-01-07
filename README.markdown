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
   4. not be assigned more than `R` roles in total
   5. not be in the same team as anyone on their shift

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

Run `demo.py` for an example with 6 weeks:

```
> python3 demo.py
GLPSOL: GLPK LP/MIP Solver, v4.65
Parameter(s) specified in the command line:
 --cpxlp /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/24d64a458b9541f2b0455378c8e174a2-pulp.lp
 -o /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/24d64a458b9541f2b0455378c8e174a2-pulp.sol
Reading problem data from '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/24d64a458b9541f2b0455378c8e174a2-pulp.lp'...
1801 rows, 600 columns, 9495 non-zeros
600 integer variables, all of which are binary
9749 lines were read
GLPK Integer Optimizer, v4.65
1801 rows, 600 columns, 9495 non-zeros
600 integer variables, all of which are binary
Preprocessing...
641 rows, 250 columns, 3559 non-zeros
250 integer variables, all of which are binary
Scaling...
 A: min|aij| =  1.000e+00  max|aij| =  1.000e+00  ratio =  1.000e+00
Problem data seem to be well scaled
Constructing initial basis...
Size of triangular part is 545
Solving LP relaxation...
GLPK Simplex Optimizer, v4.65
641 rows, 250 columns, 3559 non-zeros
      0: obj =  -0.000000000e+00 inf =   1.020e+02 (52)
     76: obj =   5.125000000e+00 inf =   8.771e-15 (0)
*   172: obj =   1.600000000e+01 inf =   3.462e-14 (0) 1
OPTIMAL LP SOLUTION FOUND
Integer optimization begins...
Long-step dual simplex will be used
+   172: mip =     not found yet <=              +inf        (1; 0)
+   294: >>>>>   1.500000000e+01 <=   1.600000000e+01   6.7% (15; 0)
+   319: >>>>>   1.600000000e+01 <=   1.600000000e+01   0.0% (6; 18)
+   319: mip =   1.600000000e+01 <=     tree is empty   0.0% (0; 31)
INTEGER OPTIMAL SOLUTION FOUND
Time used:   0.0 secs
Memory used: 1.9 Mb (2043824 bytes)
Writing MIP solution to '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/24d64a458b9541f2b0455378c8e174a2-pulp.sol'...

== Week 1:
PRIMARY: Randell Gingras
SECONDARY: Lucile Spanbauer
SHADOW: Jessie Ahlquist
PRIMARY_ONCALL: Katerine Greenwood
SECONDARY_ONCALL: Arlette Mckeighan

== Week 2:
PRIMARY: Helen Jarrard
SECONDARY: Brant Paskett
SHADOW: Santiago Mizer
PRIMARY_ONCALL: Theodore Hagberg
SECONDARY_ONCALL: Gussie Fridley

== Week 3:
PRIMARY: Don Mong
SECONDARY: Camille Whitmarsh
SHADOW: Jessie Ahlquist
PRIMARY_ONCALL: Buffy Nowacki
SECONDARY_ONCALL: Arlette Mckeighan

== Week 4:
PRIMARY: Leticia Grable
SECONDARY: Lucile Spanbauer
SHADOW: Elvira Stefani
PRIMARY_ONCALL: Theodore Hagberg
SECONDARY_ONCALL: Eleni Brandy

== Week 5:
PRIMARY: Randell Gingras
SECONDARY: Verda Streit
SHADOW: Santiago Mizer
PRIMARY_ONCALL: Katerine Greenwood
SECONDARY_ONCALL: Helen Jarrard

== Week 6:
PRIMARY: Leticia Grable
SECONDARY: Brant Paskett
SHADOW: Elvira Stefani
PRIMARY_ONCALL: Buffy Nowacki
SECONDARY_ONCALL: Camille Whitmarsh
```
