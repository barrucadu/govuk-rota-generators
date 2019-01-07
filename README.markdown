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

Run `demo.py` for an example with 6 weeks:

```
> python3 demo.py
GLPSOL: GLPK LP/MIP Solver, v4.65
Parameter(s) specified in the command line:
 --cpxlp /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/877b051632e24ca9af9ff2877413c828-pulp.lp
 -o /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/877b051632e24ca9af9ff2877413c828-pulp.sol
Reading problem data from '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/877b051632e24ca9af9ff2877413c828-pulp.lp'...
8568 rows, 2196 columns, 43848 non-zeros
2196 integer variables, all of which are binary
43555 lines were read
GLPK Integer Optimizer, v4.65
8568 rows, 2196 columns, 43848 non-zeros
2196 integer variables, all of which are binary
Preprocessing...
432 hidden packing inequaliti(es) were detected
4571 rows, 1056 columns, 21610 non-zeros
1056 integer variables, all of which are binary
Scaling...
 A: min|aij| =  1.000e+00  max|aij| =  1.000e+00  ratio =  1.000e+00
Problem data seem to be well scaled
Constructing initial basis...
Size of triangular part is 4379
Solving LP relaxation...
GLPK Simplex Optimizer, v4.65
4571 rows, 1056 columns, 21610 non-zeros
      0: obj =  -0.000000000e+00 inf =   4.420e+02 (342)
    309: obj =   8.688818182e+03 inf =   9.434e-14 (0) 1
*   577: obj =   3.601900000e+04 inf =   5.630e-14 (0) 2
OPTIMAL LP SOLUTION FOUND
Integer optimization begins...
Long-step dual simplex will be used
+   577: mip =     not found yet <=              +inf        (1; 0)
+  1015: >>>>>   3.601900000e+04 <=   3.601900000e+04 < 0.1% (42; 0)
+  1015: mip =   3.601900000e+04 <=     tree is empty   0.0% (0; 83)
INTEGER OPTIMAL SOLUTION FOUND
Time used:   0.9 secs
Memory used: 9.2 Mb (9659496 bytes)
Writing MIP solution to '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/877b051632e24ca9af9ff2877413c828-pulp.sol'...

== Week 1:
PRIMARY: Delisa Polson
SECONDARY: Verda Streit
SHADOW: Brant Paskett
PRIMARY_ONCALL: Hector Beckett
SECONDARY_ONCALL: Danielle Bence

== Week 2:
PRIMARY: Helen Jarrard
SECONDARY: Wilfredo Yoshida
SHADOW: Arlette Mckeighan
PRIMARY_ONCALL: Eleni Brandy
SECONDARY_ONCALL: Galen Takemoto

== Week 3:
PRIMARY: David Reifsteck
SECONDARY: Eura Joseph
SHADOW: Breana Mar
PRIMARY_ONCALL: Don Mong
SECONDARY_ONCALL: Danielle Bence

== Week 4:
PRIMARY: Gussie Fridley
SECONDARY: Eleni Brandy
SHADOW: Arlette Mckeighan
PRIMARY_ONCALL: Elvira Stefani
SECONDARY_ONCALL: Galen Takemoto

== Week 5:
PRIMARY: Lynn Steinhauer
SECONDARY: Santiago Mizer
SHADOW: Brant Paskett
PRIMARY_ONCALL: Eura Joseph
SECONDARY_ONCALL: Helen Jarrard

== Week 6:
PRIMARY: Galen Takemoto
SECONDARY: Hector Beckett
SHADOW: Breana Mar
PRIMARY_ONCALL: David Reifsteck
SECONDARY_ONCALL: Eleni Brandy

== Week 7:
PRIMARY: Elvira Stefani
SECONDARY: Santiago Mizer
SHADOW: Buffy Nowacki
PRIMARY_ONCALL: Danielle Bence
SECONDARY_ONCALL: Helen Jarrard

== Week 8:
PRIMARY: Gussie Fridley
SECONDARY: David Reifsteck
SHADOW: Allyson Mirando
PRIMARY_ONCALL: Hector Beckett
SECONDARY_ONCALL: Galen Takemoto

== Week 9:
PRIMARY: Elvira Stefani
SECONDARY: Verda Streit
SHADOW: Camille Whitmarsh
PRIMARY_ONCALL: Delisa Polson
SECONDARY_ONCALL: Eleni Brandy

== Week 10:
PRIMARY: Mauro Au
SECONDARY: Galen Takemoto
SHADOW: Buffy Nowacki
PRIMARY_ONCALL: Eura Joseph
SECONDARY_ONCALL: Hector Beckett

== Week 11:
PRIMARY: Werner Rosenblatt
SECONDARY: Eleni Brandy
SHADOW: Allyson Mirando
PRIMARY_ONCALL: David Reifsteck
SECONDARY_ONCALL: Elvira Stefani

== Week 12:
PRIMARY: Hector Beckett
SECONDARY: Wilfredo Yoshida
SHADOW: Camille Whitmarsh
PRIMARY_ONCALL: Eura Joseph
SECONDARY_ONCALL: Don Mong
```
