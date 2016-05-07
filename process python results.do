clear all
version 14

* read in data from python
* cluster level, includes area of convex hull
insheet using "$dir\python\cluster_level_results.csv", clear
drop if _n==2
drop if _n==1
rename v1 id
d

* deal with python's 2 level var names
rename state maxstate
rename v4 minstate
rename lga minlga
rename v6 maxlga
rename team minteam
rename v9 maxteam

destring huct, replace
destring minstate, replace
destring maxstate, replace
destring minteam, replace
destring maxteam, replace

* team level indicator
egen iteam = tag(minteam)

save clusters, replace


use clusters, replace

sum area, det

gr box area
 
* random effects by team 
mixed area huct minstate || minteam:
est sto m1

* random effects by team, random slope on huct
mixed area huct minstate || minteam: huct
est sto m2

* random slopes model fits much better
lrtest m2 m1

* predict random effects for each team
predict re_team*, reffects

* reduce to team level data set
keep if iteam

* re_team1 is random slope on huct
* re_team2 is random intercept
d re_team*
sum re_team1, det

kdens re_team1,	xline(0) xtitle("Team-level Random Slopes") ///
	scheme(s1mono)
gr export "dist of team eblups.png", replace

