param nV;
/*  Number of vertex*/

param nF;
/*  Number of faces*/

set V := 1..nV;
/* Set of vertex */
set F := 1..nF;

set M, within V cross F;
/* Visibility Matrx -> for each vertex nF columns*/

param visible{(v,f) in M}, binary;
/* 1 if vertex i can see face j, 0 otherwise*/

var chosen{v in V}, binary;
/* 1 if vertex v is chosen, 0 otherwise*/

minimize total: sum{v in V} chosen[v];

s.t. cond{f in F}: sum{(v,f) in M} visible[v,f] * chosen[v] >= 1; 


data;
param nV := 12;
param nF := 7;

param : M : visible:=
	1 1 1
	1 2 1
1 3 1
1 4 0
1 5 0
1 6 0
1 7 0
2 1 1
2 2 1
2 3 1
2 4 0
2 5 0
2 6 0
2 7 0
3 1 1
3 2 1
3 3 1
3 4 1
3 5 1
3 6 0
3 7 0
4 1 0
4 2 1
4 3 0
4 4 1
4 5 1
4 6 0
4 7 0
5 1 0
5 2 0
5 3 0
5 4 0
5 5 1
5 6 1
5 7 1
6 1 0
6 2 0
6 3 0
6 4 0
6 5 1
6 6 1
6 7 1
7 1 0
7 2 0
7 3 0
7 4 0
7 5 1
7 6 1
7 7 1
8 1 0
8 2 0
8 3 0
8 4 0
8 5 1
8 6 1
8 7 1
9 1 0
9 2 1
9 3 0
9 4 1
9 5 0
9 6 1
9 7 1
10 1 1
10 2 1
10 3 1
10 4 1
10 5 1
10 6 0
10 7 0
11 1 1
11 2 1
11 3 1
11 4 0
11 5 0
11 6 0
11 7 0
12 1 1
12 2 1
12 3 1
12 4 0
12 5 0
12 6 0
12 7 0
;
end;