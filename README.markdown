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
   6. not be in the same team as anyone on their shift

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
 --cpxlp /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/f3a48939985846f58568342b384abf09-pulp.lp
 -o /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/f3a48939985846f58568342b384abf09-pulp.sol
Reading problem data from '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/f3a48939985846f58568342b384abf09-pulp.lp'...
1955 rows, 620 columns, 10345 non-zeros
620 integer variables, all of which are binary
10477 lines were read
GLPK Integer Optimizer, v4.65
1955 rows, 620 columns, 10345 non-zeros
620 integer variables, all of which are binary
Preprocessing...
93 hidden packing inequaliti(es) were detected
1 hidden covering inequaliti(es) were detected
763 rows, 258 columns, 3757 non-zeros
258 integer variables, all of which are binary
Scaling...
 A: min|aij| =  1.000e+00  max|aij| =  1.000e+00  ratio =  1.000e+00
Problem data seem to be well scaled
Constructing initial basis...
Size of triangular part is 667
Solving LP relaxation...
GLPK Simplex Optimizer, v4.65
763 rows, 258 columns, 3757 non-zeros
      0: obj =   1.000000000e+03 inf =   1.590e+02 (85)
     99: obj =   8.176166667e+03 inf =   6.273e-15 (0)
*   205: obj =   2.001800000e+04 inf =   2.819e-14 (0) 1
OPTIMAL LP SOLUTION FOUND
Integer optimization begins...
Long-step dual simplex will be used
+   205: mip =     not found yet <=              +inf        (1; 0)
+   275: >>>>>   2.001800000e+04 <=   2.001800000e+04   0.0% (6; 0)
+   275: mip =   2.001800000e+04 <=     tree is empty   0.0% (0; 11)
INTEGER OPTIMAL SOLUTION FOUND
Time used:   0.0 secs
Memory used: 2.1 Mb (2189864 bytes)
Writing MIP solution to '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/f3a48939985846f58568342b384abf09-pulp.sol'...

== Week 1:
PRIMARY: Don Mong
SECONDARY: Nathanael Mejia
SHADOW: Arlette Mckeighan
PRIMARY_ONCALL: Jessie Ahlquist
SECONDARY_ONCALL: Verda Streit

== Week 2:
PRIMARY: Gussie Fridley
SECONDARY: Katerine Greenwood
SHADOW: Randell Gingras
PRIMARY_ONCALL: Santiago Mizer
SECONDARY_ONCALL: Buffy Nowacki

== Week 3:
PRIMARY: Don Mong
SECONDARY: Nathanael Mejia
SHADOW: Jessie Ahlquist
PRIMARY_ONCALL: Lucile Spanbauer
SECONDARY_ONCALL: Leticia Grable

== Week 4:
PRIMARY: Brant Paskett
SECONDARY: Danielle Bence
SHADOW: Buffy Nowacki
PRIMARY_ONCALL: Arlette Mckeighan
SECONDARY_ONCALL: Camille Whitmarsh

== Week 5:
PRIMARY: Santiago Mizer
SECONDARY: Katerine Greenwood
SHADOW: Randell Gingras
PRIMARY_ONCALL: Jessie Ahlquist
SECONDARY_ONCALL: Helen Jarrard

== Week 6:
PRIMARY: Brant Paskett
SECONDARY: Danielle Bence
SHADOW: Buffy Nowacki
PRIMARY_ONCALL: Arlette Mckeighan
SECONDARY_ONCALL: Leticia Grable
```
