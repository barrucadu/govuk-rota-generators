Rotas
=====

For further information, see

- [Solving Scheduling Problems with Integer Linear Programming](https://memo.barrucadu.co.uk/scheduling-problems.html)
- [Conference Scheduler](https://conference-scheduler.readthedocs.io/en/latest/index.html)
- [Integer programming (wikipedia)](https://en.wikipedia.org/wiki/Integer_programming)

The basic rota model and constraints are impemented in
`rota/__init__.py`.


Mathematical model
------------------

A rota is modelled mathematically as an integer linear program: a set
of integer-valued variables with linear constraints, for which we want
to find an assignment of values to variables which meets the
constraints.

A rota has:

- A set of time slots or periods, `T`
- A set of poeple, `P`
- A set of roles, `R`

We define a collection of binary variables `A[t,p,r]`.  We interpret
such a variable having the value 1 to mean "in time slot `t`, person
`p` is assigned to role `r`".

We also want to know if a person has been assigned a role in the rota
at all, so we define a collection of binary variables `X[p]`. We
interpret such a variable having the value 1 to mean "person `p` has
at least one role assignment."

The generic way to solve a rota problem is to create these variables,
add some standard constraints (following section) and some
rota-specific constraints (eg, as documented in `2ndline.md`), and
then get an ILP solver to find an assignment of the `A` variables.



Standard constraints
--------------------

There are some constraints that every rota has:

1. In every time slot, each (mandatory) role is assigned to exactly one person:

    ```
    forall t, r if mandatory?(r); sum{p} A[t,p,r] = 1
    ```

2. In every time slot, each (optional) role is assigned to at most one person:

    ```
    forall t, r if not mandatory?(r); sum{p} A[t,p,r] <= 1
    ```

3. Nobody is assigned multiple roles in the same time slot:

    ```
    forall t, p; sum{r} A[t,p,r] <= 1
    ```

4. Nobody is assigned a role in a slot they are unavailable for:

    ```
    forall p, t if unavailable?(p), r; [t,p,r] = 0
    ```

We also need a pair of constraints to ensure that the `X[p]` variable
tracks whether someone has been assigned:

```
forall t, p, r; X[p] >= A[t,p,r]
forall p; X[p] <= sum{t, r} [t,p,r]
```
