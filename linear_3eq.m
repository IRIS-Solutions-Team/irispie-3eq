

close all
clear

m = Model.fromFile("linear_3eq.matlab", linear=true, growth=true, std=0);

parameters = jsondecode(fileread("parameters.json"));

m = assign(m, parameters);

m = solve(m);
m = steady(m);

d = struct();
% d.obs_y = Series(2:8, 1);
d.obs_cpi = Series(1, 1);

c = acf(m);
select = ["y_gap", "diff_cpi", "cpi"];
c(select, select, 1)

f = kalmanFilter(m, d, 1:1, relative=false, output="pred,filter,smooth");

