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
 --cpxlp /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/03403d62a1d249538c54902180123d0f-pulp.lp
 -o /var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/03403d62a1d249538c54902180123d0f-pulp.sol
Reading problem data from '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/03403d62a1d249538c54902180123d0f-pulp.lp'...
11796 rows, 4788 columns, 52812 non-zeros
4788 integer variables, 3492 of which are binary
56098 lines were read
GLPK Integer Optimizer, v4.65
11796 rows, 4788 columns, 52812 non-zeros
4788 integer variables, 3492 of which are binary
Preprocessing...
432 hidden packing inequaliti(es) were detected
847 constraint coefficient(s) were reduced
5821 rows, 2432 columns, 28757 non-zeros
2432 integer variables, 1852 of which are binary
Scaling...
 A: min|aij| =  1.000e+00  max|aij| =  4.500e+01  ratio =  4.500e+01
GM: min|aij| =  4.617e-01  max|aij| =  2.166e+00  ratio =  4.690e+00
EQ: min|aij| =  2.132e-01  max|aij| =  1.000e+00  ratio =  4.690e+00
2N: min|aij| =  2.500e-01  max|aij| =  1.625e+00  ratio =  6.500e+00
Constructing initial basis...
Size of triangular part is 5629
Solving LP relaxation...
GLPK Simplex Optimizer, v4.65
5821 rows, 2432 columns, 28757 non-zeros
      0: obj =  -0.000000000e+00 inf =   7.295e+02 (435)
    915: obj =   1.079737500e+04 inf =   3.351e-14 (0) 5
*  1267: obj =   3.603400000e+04 inf =   2.514e-13 (0) 3
OPTIMAL LP SOLUTION FOUND
Integer optimization begins...
Long-step dual simplex will be used
+  1267: mip =     not found yet <=              +inf        (1; 0)
Solution found by heuristic: 36034
+  2344: mip =   3.603400000e+04 <=     tree is empty   0.0% (0; 127)
INTEGER OPTIMAL SOLUTION FOUND
Time used:   5.1 secs
Memory used: 12.5 Mb (13089158 bytes)
Writing MIP solution to '/var/folders/7v/3zz_qp2x7d51b4bp2_cg0fgh0000l2/T/03403d62a1d249538c54902180123d0f-pulp.sol'...

== Week 1:
PRIMARY: Kristen Youngren Person(team='F', can_do_inhours=True, num_times_inhours=7, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SECONDARY: Isaura Lafuente Person(team='C', can_do_inhours=True, num_times_inhours=0, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SHADOW: Brant Paskett Person(team='A', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Gussie Fridley Person(team='E', can_do_inhours=True, num_times_inhours=23, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Delisa Polson Person(team='E', can_do_inhours=True, num_times_inhours=25, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 2:
PRIMARY: Eura Joseph Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
SECONDARY: Danielle Bence Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
SHADOW: Camille Whitmarsh Person(team='B', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: David Reifsteck Person(team='B', can_do_inhours=True, num_times_inhours=20, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Elvira Stefani Person(team='D', can_do_inhours=True, num_times_inhours=18, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])

== Week 3:
PRIMARY: Kristyn Wolverton Person(team='C', can_do_inhours=True, num_times_inhours=17, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SECONDARY: Brant Paskett Person(team='A', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SHADOW: Arlette Mckeighan Person(team='B', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Eleni Brandy Person(team='B', can_do_inhours=True, num_times_inhours=12, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Helen Jarrard Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 4:
PRIMARY: Kristen Youngren Person(team='F', can_do_inhours=True, num_times_inhours=7, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SECONDARY: Isaura Lafuente Person(team='C', can_do_inhours=True, num_times_inhours=0, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SHADOW: Allyson Mirando Person(team='D', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Don Mong Person(team='B', can_do_inhours=True, num_times_inhours=14, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Danielle Bence Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 5:
PRIMARY: Buffy Nowacki Person(team='D', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SECONDARY: Helen Jarrard Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
SHADOW: Camille Whitmarsh Person(team='B', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Gussie Fridley Person(team='E', can_do_inhours=True, num_times_inhours=23, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Delisa Polson Person(team='E', can_do_inhours=True, num_times_inhours=25, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 6:
PRIMARY: Katerine Greenwood Person(team='C', can_do_inhours=True, num_times_inhours=3, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SECONDARY: Wilfredo Yoshida Person(team='E', can_do_inhours=True, num_times_inhours=1, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SHADOW: Allyson Mirando Person(team='D', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Eleni Brandy Person(team='B', can_do_inhours=True, num_times_inhours=12, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Danielle Bence Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 7:
PRIMARY: Don Mong Person(team='B', can_do_inhours=True, num_times_inhours=14, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY: Santiago Mizer Person(team='E', can_do_inhours=True, num_times_inhours=0, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SHADOW: Buffy Nowacki Person(team='D', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Elvira Stefani Person(team='D', can_do_inhours=True, num_times_inhours=18, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Eura Joseph Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 8:
PRIMARY: David Reifsteck Person(team='B', can_do_inhours=True, num_times_inhours=20, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY: Verda Streit Person(team='E', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Eleni Brandy Person(team='B', can_do_inhours=True, num_times_inhours=12, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Delisa Polson Person(team='E', can_do_inhours=True, num_times_inhours=25, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 9:
PRIMARY: Leticia Grable Person(team='B', can_do_inhours=True, num_times_inhours=19, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SECONDARY: Helen Jarrard Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
SHADOW: Breana Mar Person(team='A', can_do_inhours=True, num_times_inhours=0, num_times_shadow=1, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Don Mong Person(team='B', can_do_inhours=True, num_times_inhours=14, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Danielle Bence Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])

== Week 10:
PRIMARY: Galen Takemoto Person(team='B', can_do_inhours=True, num_times_inhours=12, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
SECONDARY: Wilfredo Yoshida Person(team='E', can_do_inhours=True, num_times_inhours=1, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Elvira Stefani Person(team='D', can_do_inhours=True, num_times_inhours=18, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: David Reifsteck Person(team='B', can_do_inhours=True, num_times_inhours=20, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])

== Week 11:
PRIMARY: Werner Rosenblatt Person(team='A', can_do_inhours=True, num_times_inhours=24, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SECONDARY: Nathanael Mejia Person(team='D', can_do_inhours=True, num_times_inhours=1, num_times_shadow=2, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
SHADOW: Arlette Mckeighan Person(team='B', can_do_inhours=True, num_times_inhours=0, num_times_shadow=0, can_do_oncall=False, num_times_oncall=0, forbidden_weeks=[])
PRIMARY_ONCALL: Don Mong Person(team='B', can_do_inhours=True, num_times_inhours=14, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Gussie Fridley Person(team='E', can_do_inhours=True, num_times_inhours=23, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])

== Week 12:
PRIMARY: Delisa Polson Person(team='E', can_do_inhours=True, num_times_inhours=25, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
SECONDARY: Eura Joseph Person(team='A', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
SHADOW: Danielle Bence Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
PRIMARY_ONCALL: David Reifsteck Person(team='B', can_do_inhours=True, num_times_inhours=20, num_times_shadow=2, can_do_oncall=True, num_times_oncall=2, forbidden_weeks=[])
SECONDARY_ONCALL: Helen Jarrard Person(team='C', can_do_inhours=True, num_times_inhours=2, num_times_shadow=2, can_do_oncall=True, num_times_oncall=3, forbidden_weeks=[])
```
