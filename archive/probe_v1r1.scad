// ============================================================
// sub-mission probe v1 — REVISED after gemini review round 1
// Fixes applied:
// F1 rotor shaft+bearings added; wet cup runs on its own mini-shaft
//    carried by a PEEK bushing in the pod nose; magnetic axial preload
//    balanced by a thrust collar.
// F4 river() depth to 1200mm so pod at -420 is truly in water.
// F6 weed/debris guard ring upstream of rotor + debris vane.
// F8 supercap overvoltage clamp (TL431 clamp + dump resistor) noted
//    in design + scad placeholder.
// F2 cut-in: sim now models stalled-blade static torque (see sim v2).
// ============================================================
use <naca4412.scad>
$fn = 96;

rotor_d = 220;  rotor_r = rotor_d/2;
hub_d = 64; hub_len = 46;
blade_n = 3; pitch_deg = 28; root_cut = 22;
stations = [
  [ root_cut/rotor_r, 42, 28 ],  // root: high pitch for stall-start authority
  [ 0.40, 38, 20 ],
  [ 0.55, 34, 12 ],
  [ 0.70, 30,  6 ],
  [ 0.85, 24,  3 ],
  [ 1.00, 17,  2 ],             // tip: alpha_tip ~5deg at TSR 5.5
];
magcup_gap=5; magcup_d=42; magcup_h=14; mag_d=8; mag_h=5; mag_n=8;
pod_od=110; pod_id=96; pod_len=120;
cage_len=150; cage_od=130; cage_wall=4; cage_slots=12;
arm_od=28; arm_end_x=1200; arm_z=60;
pole_od=60; pole_h=2600;
box_w=190; box_d=130; box_h=80; deck_z=1750;
pod_depth=420;

module tube(od,id,h){difference(){cylinder(d=od,h=h);translate([0,0,-1])cylinder(d=id,h=h+2);}}

module blade(){
  nsec=len(stations)-1;
  for(i=[0:nsec-1]){
    r0=stations[i][0]*rotor_r; c0=stations[i][1]; t0=stations[i][2];
    r1=stations[i+1][0]*rotor_r; c1=stations[i+1][1]; t1=stations[i+1][2];
    hull(){
      translate([r0,0,0]) rotate([0,-t0,0]) scale([c0,c0,1])
        linear_extrude(0.1) polygon(naca4412_pts(24));
      translate([r1,0,0]) rotate([0,-t1,0]) scale([c1,c1,1])
        linear_extrude(0.1) polygon(naca4412_pts(24));
    }
  }
}

// wet rotor with its own shaft and 2 bearings (MR105zz 5x10x4 or PEEK equiv)
module rotor_axis_z(){
  color("darkorange") cylinder(d=hub_d, h=hub_len, center=true);
  for(i=[0:blade_n-1]) rotate([0,0,i*360/blade_n]) color("steelblue") blade();
  // shaft out the back
  color("gainsboro") translate([0,0,-hub_len/2-26]) cylinder(d=5, h=30, $fn=20);
}

// bearing journal housing in the pod nose; PEEK bushings x2
module nose_bearings(){
  color("tan") translate([0,0,-30]) cylinder(d=22, h=14);      // front bushing block
  color("tan") translate([0,0,-12]) cylinder(d=22, h=10);      // rear bushing block
}

module magnet_ring_z(){
  for(i=[0:mag_n-1]) rotate([0,0,i*360/mag_n])
    translate([magcup_d/2-mag_d, 0, magcup_h/2+1])
      // each magnet hermetically canned (F10 fix: stainless can)
      color("silver") difference(){
        cylinder(d=mag_d+1, h=mag_h+1, center=true, $fn=20);
        cylinder(d=mag_d-0.1, h=mag_h+0.1, center=true, $fn=20);
      }
}
module magcup_z(){
  color("dimgray"){
    cylinder(d=magcup_d, h=3);
    translate([0,0,3]) difference(){cylinder(d=magcup_d+6,h=magcup_h-3);
      translate([0,0,-1])cylinder(d=magcup_d,h=magcup_h);}
  }
  magnet_ring_z();
}

// weed guard ring upstream of the rotor (F6)
module weed_guard(){
  color("forestgreen",0.85)
  translate([0,0,-40])  // 40mm ahead of blade plane
    difference(){
      cylinder(d=rotor_d+30, h=4, $fn=96);
      cylinder(d=rotor_d+8, h=6, $fn=96);
    }
  // three struts from pod nose to ring
  for(i=[0:2]) rotate([0,0,i*120+30])
    color("forestgreen",0.85)
      translate([(rotor_d+18)/2, 0, -38])
        cube([16, 10, 40], center=false);
}

module genpod_z(){
  difference(){
    color("seagreen"){
      cylinder(d=pod_od, h=pod_len);
      translate([0,0,pod_len]) scale([1,1,0.55]) sphere(d=pod_od, $fn=64);
    }
    translate([0,0,-1]) cylinder(d=pod_id, h=pod_len+pod_od);
  }
  color("seagreen") translate([0,0,-magcup_gap]) cylinder(d=pod_od-4, h=magcup_gap);
  color("gray") translate([0,0,30]) cube([44,44,60], center=true);
  color("gray") translate([0,0,2]) cylinder(d=10, h=28); // gen shaft
  translate([0,0,-magcup_gap-magcup_h]) magcup_z();      // dry cup
  // clamp electronics block (TL431 + dump R) — F8 placeholder
  color("darkred") translate([25,0,60]) cube([22,18,10], center=true);
}

module rotorside_z(){
  translate([0,0,-magcup_gap-2*magcup_h-4]) rotate([180,0,0]) magcup_z();
  color("darkorange")
    translate([0,0,-magcup_gap-2*magcup_h-8]) cylinder(d=magcup_d+10, h=6);
  nose_bearings();
}

module sensor_cage_z(){
  color("royalblue",0.9) difference(){
    cylinder(d=cage_od,h=cage_len);
    translate([0,0,-1])cylinder(d=cage_od-2*cage_wall,h=cage_len+2);
    for(i=[0:cage_slots-1]) rotate([0,0,i*360/cage_slots])
      translate([cage_od/2,0,cage_len/2]) cube([cage_od,8,cage_len*0.7],center=true);
    translate([0,0,-1])cylinder(d=cage_od*0.5,h=3);
    translate([0,0,cage_len-2])cylinder(d=cage_od*0.5,h=3);
  }
  color("white"){
    translate([35,0,30]) cylinder(d=12,h=80);
    translate([-35,0,40]) cylinder(d=18,h=60);
    translate([0,35,70]) cube([34,26,22], center=true);
    translate([0,-35,30]) cylinder(d=6,h=60);
    translate([20,-20,60]) color("lightgray") cube([50,40,30], center=true);
  }
}

module wetpod_z(){
  rotor_axis_z();
  translate([0,0,hub_len/2+6]) rotorside_z();
  translate([0,0,hub_len/2+6]) genpod_z();
  weed_guard();
  translate([0,0,hub_len/2+6+pod_len+magcup_gap+60]) sensor_cage_z();
}

module site(){
  color("dimgray") cylinder(d=pole_od,h=pole_h,$fn=48);
  color("black") translate([0,0,arm_z-22]) cylinder(d=pole_od+16,h=44,$fn=48);
  color("darkgray") translate([0,0,arm_z]) rotate([0,85,0]) cylinder(d=arm_od,h=arm_end_x+40);
  color("darkgray") translate([arm_end_x,0,arm_z+arm_end_x*tan(5)]) sphere(d=arm_od+8,$fn=28);
  // drop tube + downstream yaw strut to stop swing (F12)
  arm_end_z = arm_z + arm_end_x*tan(5);
  color("darkgray") translate([arm_end_x,0,-pod_depth]) cylinder(d=arm_od-6,h=arm_end_z+pod_depth,$fn=32);
  color("darkgray") translate([arm_end_x, 0, arm_end_z-6]) rotate([0,90,0]) cylinder(d=arm_od-10,h=260); // horizontal strut downstream
  color("khaki")     translate([0,0,deck_z]) cube([box_d+30,box_w,box_h],center=true);
  color("darkkhaki") translate([0,0,deck_z+box_h/2]) cube([box_d+32,box_w+2,6],center=true);
  color("black")     translate([0,0,deck_z+box_h/2]) cylinder(d=6,h=330);
  color("crimson")   translate([0,0,deck_z+box_h/2+330]) sphere(d=9);
  color("black") translate([-(pole_od/2+5),0,arm_z+30]) cylinder(d=9,h=deck_z-box_h/2-arm_z-30);
}

module river(){
  // water 1.2 m deep so pod at -420mm is mid-column (F4 fix)
  color("deepskyblue",0.30) translate([-200,-900,-1200]) cube([2100,1800,1200]);
  color("saddlebrown")      translate([-200,-900,-1260]) cube([2100,1800,60]);
  color("darkgreen")        translate([-400,-900,-1260]) cube([210,1800,1300]);
}

module full(){
  translate([arm_end_x,0,-pod_depth]) rotate([0,-90,0]) wetpod_z();
  site();
}

mode=0;
if (mode==0){ full(); river(); }
if (mode==1){ full(); }
if (mode==2){ wetpod_z(); }
if (mode==3){ rotor_axis_z(); translate([0,0,160]) rotorside_z();
              translate([0,0,300]) genpod_z(); translate([0,0,540]) sensor_cage_z(); }
