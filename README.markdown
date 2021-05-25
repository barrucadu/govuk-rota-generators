govuk-rota-generators
=====================

It does what it says on the tin.

```
$ python3 src
Usage:
  cli.py <file> [--num-weeks=<n>] [--max-in-hours-shifts=<n>] [--max-on-call-shifts=<n>]
  cli.py (-h | --help)

$ time python3 src demo.csv
week,primary,secondary,shadow,primary_oncall,secondary_oncall
1,Neil Hockenberry,Aubrey Staiger,Sharleen Woltz,Oswaldo Bonham,Jarrett Hord
2,Deloris Baldon,Rocco Morra,,Martin Ashby,Robin Hoose
3,Emanuel Leinen,Vernon Minelli,,Lou Meidinger,Renae Paton
4,Floyd Olsson,Irwin Capehart,,Dewey Burgett,Jerold Bayes
5,Pierre Paulhus,Sammie Shew,,Lou Meidinger,Wilson Friesen
6,Jerome Silveria,Benita Kunz,Glynda Laubscher,Oswaldo Bonham,Temeka Lowy
7,Jame Truss,Nyla Drozd,,Annalisa Harrow,Renae Paton
8,Ryan Averett,Jerald Vangundy,,Jeannine Demos,Jerold Bayes
9,Theodore Calvery,Temeka Lowy,Chas Stucky,Dave Allred,Grant Kornfeld
10,Martin Ashby,Lacy Auyeung,Ramon Haddock,Annalisa Harrow,Oswaldo Bonham
11,Bessie Engebretson,Wilson Friesen,,Jeannine Demos,Jerold Bayes
12,Dave Allred,Lou Meidinger,,Annalisa Harrow,Santiago Raine

real    0m24.531s
user    0m24.408s
sys     0m0.121s
```

See the `docs` directory for explanations of how the rotas are defined
and generated.


Dependencies
------------

You need [Cbc][] (**C**oin-or **b**ranch and **c**ut) installed and in
your `$PATH`.  Other dependencies are listed in
`requirements-freeze.txt` and can be installed with `pip`.

[Cbc]: https://projects.coin-or.org/Cbc

### Running in Docker

Rather than install dependencies to your host machine, you can
generate a rota in a Docker container:

```bash
$ docker run -it --rm -v $(pwd):/src -w /src python:3.9 bash
$ apt-get update && apt-get install -y coinor-cbc
$ pip install -r requirements-freeze.txt
$ python3 src demo.csv
```


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
