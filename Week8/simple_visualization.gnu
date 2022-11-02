reset session
set parametric
set size ratio -1
set xrange [*<-1.5:1.5<*]
set yrange [*<-1.5:1.5<*]
set object 1 rect from -1,-1 to 1,1
set object 2 rect from -0.8,0.4 to 0.8,0.8
set object 3 rect from -0.8,-0.8 to 0.8,-0.4
plot "trajectory.dat" with vectors title "robot trajectory"
