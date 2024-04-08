

close all
clear

m = Model4Py.fromFile("linear_3eq.matlab", linear=true, growth=true, std=0);

parameters = jsondecode(fileread("parameters.json"));

m = assign(m, parameters);

m = solve(m);
m = steady(m);



start_filt = qq(2021,1);
end_filt = qq(2022,4);
filt_span = start_filt : end_filt;

% obs_db = struct();
% values = [1.20; 1.03; 0.91; 1.97; 0.32; 0.91; 1.41; 1.48];
% obs_db.obs_y = Series(start_filt, values);
% obs_db.obs_cpi = Series(start_filt, [10; NaN; 12]);

obs_db = databank.fromSheet("obs_db.csv", includeComments=false);
obs_db = databank.clip(obs_db, filt_span);

obs_db = struct()
obs_db.obs_cpi = Series(start_filt, [0;0]);

f = kalmanFilter( ...
    m, obs_db, start_filt:start_filt+3 ...
    , relative=false ...
    , output="pred,filter,smooth" ...
    , meanOnly=true ...
);

% p = f.Predict.Mean;
% d = f.Smooth.Mean;
% disp([p.y_tnd, p.y_gap])
% disp([d.y_tnd, d.y_gap, d.y_tnd + d.y_gap, obs_db.obs_y])
% disp([d.cpi]);


