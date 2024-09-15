# Pre-season planning
The season's released but we don't have the field yet, it's almost midnight on a Saturday and I started thinking. So, here's the goals I have for the auto, the features needed to implement them, and an order in which they could happen. 

The gist of this document is that I really don't like the control system from last year. It works, but it's hacked together and it's difficult to debug, and I don't think it'll hold up to what I want to get out of it this season. I want to do a big refactor, this time with proper validation of how good each component is.

(also, to whoever's reading this at the end of the season, how much did I stick to the plan?)

## Goals and Features
### Goal: Better logging
* Feature: Data logging straight to a file. Get rid of the old bad multiprocessing-based queue system and make a new one that's totally separate from the main program and pulls from that file. On-purpose side effect: file is also saved for later analysis.
* Feature: Rough out a 3D model of the field and be able to replay flights in 3d, like MeepMeep but post-run.
### Goal: Ability to evaluate state estimation and system control separately
* Feature: Make a way to move drone along consistent trajectory (repeatable displacement, velocity, and acceleration) in different axes, use that for verifying drone sensors.
* Task: Characterize drone response to inputs. Variables: axis, input magnitude, battery level. Ideally do this semi-automated with a validated state estimation model.
* Feature: Make a way to evaluate how good a controller is. Maybe integral of magnitude of error for some canonical set of moves?
### Goal: Reduce position oscillation
* Task: See if sendControlPosition or gotoWaypoint gives better results than my loops.
* Feature: Switch to [Proportional-On-Measurement](http://brettbeauregard.com/blog/2017/06/introducing-proportional-on-measurement/) PID loops to reduce overshoot
* Feature: Use specific sensor calls instead of get_sensor_data to speed up control rate (should get us from 20hz to 30+, as long as the bottleneck is latency, not drone-side sensor polling rate)
### Goal: Be faster
reasoning: ideal mission time is <1:25

tradeoff: harder to control, likely increased rate of compounding error

* Feature: Use undocumented change_speed function to live on Speed 3 as much as possible instead of default Speed 2
### Goal: Separate z-displacement from distance above ground
reasoning: we can use the range sensor to tell when we're over the landing boxes

* Task: Test if barometric altitude is significantly worse than bottom range altitude.
    * If barometric is worse: For control purposes, rely primarily on bottom range data, but when there's a spike, use the _changes_ from the barometric altitude to estimate.
    * If barometric is equal or better: Use barometric for z-displacement, use bottom range data for AGL.

## Prioritizing
1. New data logging and live graphing.
2. Build state estimation test rig.
3. Test barometric altitude vs. range altitude up to 2m ΔZ (likely ceiling of 1.5m plus wiggle room)
4. Build and validate state estimation model (incl. separation of AGL and ΔZ), ideally at multiple speeds.
5. Characterize drone flight. See if thrust-vectoring-based model is accurate. (i.e. shouldn't we just be able to do a_x=F_props*cos(θ_pitch)/m_drone etc., and even work backwards to determine F_props empirically?)
6. Develop controller evaluation.
7. Evaluate current controller, as a baseline.
8. Evaluate sendControlPosition and goToWaypoint.
9. Evaluate PonM-tuned controller, if promising.
10. If thrust vectoring worked well, evaluate feasibility of feedforward or feedforward-assisted control.
11. Evaluate effect of high speed on controller accuracy.
12. Build 3D model and flight visualizer.

Milestone: By this point we have a reliable, precise motion system, plus diagostic tools for when things break. The hard part should be over.

13. Using our nice motion system, write a routine to do this year's autonomous mission. At this point it _should_ be as easy as just listing a bunch of waypoints, plus some sensor fun for the landing and (maybe) the holes.
