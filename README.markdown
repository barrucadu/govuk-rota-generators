govuk-rota-generators
=====================

It does what it says on the tin.


```
$ python3 src
Usage:
  cli.py <file> [--num-weeks=<n>] [--max-in-hours-shifts=<n>] [--max-on-call-shifts=<n>]
  cli.py (-h | --help)

$ time ./cli.py demo.csv
week,primary,secondary,shadow,primary_oncall,secondary_oncall
1,Annalisa Harrow,Temeka Lowy,,Jerome Silveria,Dave Allred
2,Renae Paton,Wilson Friesen,,Ryan Averett,Jerold Bayes
3,Jeannine Demos,Jerald Vangundy,,Dave Allred,Annalisa Harrow
4,Irwin Capehart,Jarrett Hord,,Lou Meidinger,Jame Truss
5,Jerome Silveria,Benita Kunz,,Dewey Burgett,Ryan Averett
6,Deloris Baldon,Emanuel Leinen,,Lou Meidinger,Annalisa Harrow
7,Dave Allred,Floyd Olsson,,Dewey Burgett,Jeannine Demos
8,Nyla Drozd,Grant Kornfeld,,Ryan Averett,Annalisa Harrow
9,Lou Meidinger,Lacy Auyeung,,Dave Allred,Oswaldo Bonham
10,Martin Ashby,Sammie Shew,Ryan Averett,Jerold Bayes,Jerome Silveria
11,Theodore Calvery,Robin Hoose,Vernon Minelli,Lou Meidinger,Dewey Burgett
12,Rocco Morra,Santiago Raine,Pierre Paulhus,Neil Hockenberry,Oswaldo Bonham

real    33.38s
user    32.99s
sys     0.36s
```

See the `docs` directory for explanations of how the rotas are defined
and generated.


Dependencies
------------

You need [Cbc][] (**C**oin-or **b**ranch and **c**ut) installed and in
your `$PATH`.  Other dependencies are listed in
`requirements-freeze.txt` and can be installed with `pip`.

[Cbc]: https://projects.coin-or.org/Cbc


Mathematical background
-----------------------

This uses an approach called [integer linear programming][] (ILP), via
the [PuLP library][].  A reasonable introduction to ILP for solving
scheduling problems like this is [the PyCon conference-scheduler
docs][].

I [wrote a memo][memo] going into some detail about how it all works.

[integer linear programming]: https://en.wikipedia.org/wiki/Integer_programming
[PuLP library]: https://pythonhosted.org/PuLP/
[the PyCon conference-scheduler docs]: https://conference-scheduler.readthedocs.io/en/latest/background/mathematical_model.html
[memo]: https://memo.barrucadu.co.uk/scheduling-problems.html
