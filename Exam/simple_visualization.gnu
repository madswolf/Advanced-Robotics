reset session
set parametric
set size ratio -1
set xrange [*<-1.5:1.5<*]
set yrange [*<-1.5:1.5<*]
set object 1 rect from -1,-1 to 1,1
set object 1 rect fc rgb "black" fillstyle solid 1.0
set object 2 rect from -0.9,-0.9 to 0.9,0.9
set object 3 rect from -0.1,-0.1 to 0.1,0.1
set object 3 rect fc rgb "gray" fillstyle solid 1.0
plot "trajectory.dat" with vectors title "robot trajectory"
