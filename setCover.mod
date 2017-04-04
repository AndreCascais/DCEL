param nV;
/*  Number of vertex*/

param nF;
/*  Number of faces*/

param nG;
/* Number of guards*/

set V := 0..(nV - 1);
/* Set of vertex */
set F := 0..(nF - 1);

set M, within V cross F;
/* Visibility Matrx -> for each vertex nF columns*/

param visible{(v,f) in M}, binary;
/* 1 if vertex i can see face j, 0 otherwise*/

var chosen{v in V}, binary;
/* 1 if vertex v is chosen, 0 otherwise*/

minimize total: sum{v in V} chosen[v];

s.t. cond{f in F}: sum{(v,f) in M} visible[v,f] * chosen[v] >= nG; 

end;

