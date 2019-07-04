govuk-rota-generators
=====================

It does what it says on the tin.


```
$ ./cli.py
Usage:
  cli.py govuk_2ndline   <file> [--num-weeks=<n>] [--max-in-hours-shifts=<n>] [--max-on-call-shifts=<n>]
  cli.py content_support <file> [--num-weeks=<n>]
  cli.py (-h | --help)

$ time ./cli.py govuk_2ndline demo.csv
week,primary,secondary,shadow,primary_oncall,secondary_oncall
1,Jerome Silveria,Grant Kornfeld,,Dewey Burgett,Dave Allred
2,Annalisa Harrow,Temeka Lowy,,Martin Ashby,Jerold Bayes
3,Lou Meidinger,Wilson Friesen,Pierre Paulhus,Ryan Averett,Jeannine Demos
4,Theodore Calvery,Emanuel Leinen,,Dave Allred,Jame Truss
5,Nyla Drozd,Jerald Vangundy,,Oswaldo Bonham,Ryan Averett
6,Jeannine Demos,Jarrett Hord,,Lou Meidinger,Dewey Burgett
7,Ryan Averett,Robin Hoose,,Neil Hockenberry,Jame Truss
8,Rocco Morra,Sammie Shew,,Lou Meidinger,Annalisa Harrow
9,Martin Ashby,Floyd Olsson,Vernon Minelli,Jerold Bayes,Jerome Silveria
10,Bessie Engebretson,Lacy Auyeung,,Jeannine Demos,Ryan Averett
11,Deloris Baldon,Benita Kunz,,Oswaldo Bonham,Neil Hockenberry
12,Irwin Capehart,Santiago Raine,,Lou Meidinger,Jerome Silveria

real    103.97s
user    101.88s
sys     1.89s
```

See the `docs` directory for explanations of how the rotas are defined
and generated.


Dependencies
------------

You need [Cbc][] (**C**oin-or **b**ranch and **c**ut) installed and in
your `$PATH`.  Other dependencies are listed in `requirements.txt` and
can be installed with `pip`.

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
