// ============================================================
// sub-mission river probe — parametric 3D model
// Bank pole + swing arm + submerged pod (mag-coupled hydro
// generator + flow-through sensor cage) + dry deck box.
// All pod parts are built COAXIAL along +Z in local space;
// the pod assembly is rotated to horizontal at the end.
// Units mm. Global axes: X downstream (flow +X), Z up.
// Water surface plane z=0. Haven, 2026-10-18.
// ============================================================

use <naca4412.scad>
$fn = 96;

// ---------------- parameters ----------------
rotor_d    = 220;  rotor_r = rotor_d/2;
hub_d      = 64;   hub_len = 46;
blade_n    = 3;
pitch_deg  = 28;
root_cut   = 22;
stations = [ // [r frac, chord mm, twist deg]
  [ root_cut/rotor_r, 42, 34 ],
  [ 0.40,             38, 30 ],
  [ 0.55,             34, 28 ],
  [ 0.70,             30, 24 ],
  [ 0.85,             24, 19 ],
  [ 1.00,             17, 13 ],
];
magcup_gap = 5;      // sealed wall between magnet cups
magcup_d   = 42;
magcup_h   = 14;
mag_d      = 8;  mag_h = 5;  mag_n = 8;
pod_od = 110;  pod_id = 96;  pod_len = 120;
nose_len = 60;
cage_len = 150;  cage_od = 130;  cage_wall = 4;  cage_slots = 12;
arm_od  = 28;  arm_len = 1500;
pole_od = 60;  pole_h  = 2600;
box_w=190; box_d=130; box_h=80;  deck_z = 1750;
pod_depth = 420;                 // rotor axis below surface

// ---------------- helpers ----------------
module tube(od,id,h){ difference(){ cylinder(d=od,h=h); translate([0,0,-1]) cylinder(d=id,h=h+2); } }

// ---------------- blade (span along +X local) ----------------
module blade() {
  nsec = len(stations)-1;
  for (i=[0:nsec-1]) {
    r0=stations[i][0]*rotor_r;  c0=stations[i][1];  t0=stations[i][2];
    r1=stations[i+1][0]*rotor_r;c1=stations[i+1][1];t1=stations[i+1][2];
    hull(){
      translate([r0,0,0]) rotate([0,-t0,0]) scale([c0,c0,1])
        linear_extrude(0.1) polygon(naca4412_pts(24));
      translate([r1,0,0]) rotate([0,-t1,0]) scale([c1,c1,1])
        linear_extrude(0.1) polygon(naca4412_pts(24));
    }
  }
}

// ---------------- rotor: hub axis along +Z (local) ----------------
module rotor_axis_z() {
  color("darkorange") cylinder(d=hub_d, h=hub_len, center=true);
  for (i=[0:blade_n-1])
    rotate([0,0, i*360/blade_n])
      color("steelblue") blade();
}

// ---------------- magnet cup (axis +Z local, base at z=0) ----------------
module magnet_ring_z() {
  for(i=[0:mag_n-1]) rotate([0,0,i*360/mag_n])
    translate([magcup_d/2-mag_d, 0, magcup_h/2+1])
      color("silver") cylinder(d=mag_d, h=mag_h, center=true, $fn=20);
}
module magcup_z() {
  color("dimgray"){
    cylinder(d=magcup_d, h=3);
    translate([0,0,3]) difference(){ cylinder(d=magcup_d+6,h=magcup_h-3); translate([0,0,-1]) cylinder(d=magcup_d,h=magcup_h); }
  }
  magnet_ring_z();
}

// ---------------- generator pod (sealed), axis +Z, base at 0 ----------------
module genpod_z() {
  difference(){
    color("seagreen"){
      cylinder(d=pod_od, h=pod_len);
      translate([0,0,pod_len]) scale([1,1,0.55]) sphere(d=pod_od,$fn=64);
    }
    translate([0,0,-1]) cylinder(d=pod_id, h=pod_len+ pod_od); // bore
  }
  // sealed front wall: the 5mm barrier the magnets couple through,
  // full pod diameter, below the barrel
  color("seagreen") translate([0,0,-magcup_gap]) cylinder(d=pod_od-4, h=magcup_gap);
  // guts
  color("gray") translate([0,0,30]) cube([44,44,60], center=true);  // motor
  color("gray") translate([0,0,2]) cylinder(d=8, h=28);             // shaft
  translate([0,0,-magcup_gap-magcup_h]) magcup_z();                 // dry-side cup (inside pod)
}

// ---------------- rotor-side: wet cup + carrier, axis +Z ----------------
module rotorside_z() {
  // wet cup: base plate toward hub, magnet rim facing the wall (downstream)
  translate([0,0,-magcup_gap-2*magcup_h-4]) rotate([180,0,0]) magcup_z();
  // carrier joining hub to wet cup
  color("darkorange")
    translate([0,0,-magcup_gap-2*magcup_h-8 ])
      cylinder(d=magcup_d+10, h=6);
}

// ---------------- sensor cage, axis +Z, base at 0 ----------------
module sensor_cage_z() {
  color("royalblue",0.9) difference(){
    cylinder(d=cage_od, h=cage_len);
    translate([0,0,-1]) cylinder(d=cage_od-2*cage_wall, h=cage_len+2);
    for(i=[0:cage_slots-1]) rotate([0,0,i*360/cage_slots])
      translate([cage_od/2,0,cage_len/2])
        cube([cage_od, 8, cage_len*0.7], center=true);
    translate([0,0,-1]) cylinder(d=cage_od*0.5, h=3);
    translate([0,0,cage_len-2]) cylinder(d=cage_od*0.5, h=3);
  }
  color("white"){
    translate([ 35,0,30]) cylinder(d=12,h=80);        // pH electrode
    translate([-35,0,40]) cylinder(d=18,h=60);        // TDS
    translate([0, 35,70]) cube([34,26,22],center=true); // turbidity head
    translate([0,-35,30]) cylinder(d=6,h=60);         // NTC pocket
    translate([20,-20,60]) color("lightgray") cube([50,40,30],center=true); // MS5837 level
  }
}

// ---------------- wet pod along +Z (rotor at bottom = upstream) ---------
module wetpod_z() {
  translate([0,0,0]) rotor_axis_z();                             // rotor at z~0
  translate([0,0,hub_len/2 + 6]) rotorside_z();                  // wet mag cup + carrier
  translate([0,0,hub_len/2 + 6]) genpod_z();                     // pod starts above wall
  translate([0,0,hub_len/2 + 6 + pod_len + magcup_gap + nose_len])
    sensor_cage_z();                                             // cage downstream
}

// ---------------- site structure ------------------------------------------------
// Layout (global, X downstream, Z up, water z=0):
//   pole at x=0 on bank edge.  Arm runs +X, 60mm above water, slightly rising.
//   At x=arm_end_x, drop tube goes down to pod_depth.
//   Pod horizontal, rotor pointing upstream (-X).
arm_end_x = 1200;   // reach out over the water
arm_z     = 60;     // above surface

module site() {
  // pole
  color("dimgray") cylinder(d=pole_od, h=pole_h, $fn=48);
  color("black")   translate([0,0,arm_z-22]) cylinder(d=pole_od+16, h=44, $fn=48); // hinge collar

  // swing arm: from collar out over water (+X), rising ~5 deg
  color("darkgray")
    translate([0,0,arm_z]) rotate([0,85,0])            // 85 deg from Z => mostly horizontal, slight rise
      cylinder(d=arm_od, h=arm_end_x+40);
  // elbow ball at end
  color("darkgray") translate([arm_end_x,0,arm_z + arm_end_x*tan(5)]) sphere(d=arm_od+8,$fn=28);

  // drop tube straight down to pod
  arm_end_z = arm_z + arm_end_x*tan(5);
  color("darkgray")
    translate([arm_end_x,0,-pod_depth])
      cylinder(d=arm_od-6, h=arm_end_z+pod_depth, $fn=32);

  // dry box on pole, high up
  color("khaki")     translate([0,0,deck_z])          cube([box_d+30, box_w, box_h], center=true);
  color("darkkhaki") translate([0,0,deck_z+box_h/2])  cube([box_d+32, box_w+2, 6], center=true);
  // 868 MHz antenna mast
  color("black")     translate([0,0,deck_z+box_h/2]) cylinder(d=6, h=330);
  color("crimson")   translate([0,0,deck_z+box_h/2+330]) sphere(d=9);
  // potted cable down the pole to the waterline
  color("black") translate([-(pole_od/2+5),0,arm_z+30]) cylinder(d=9, h=deck_z-box_h/2-arm_z-30);
}

module river() {
  color("deepskyblue",0.30) translate([-200,-900,-260]) cube([2100,1800,260]);
  color("saddlebrown")      translate([-200,-900,-300]) cube([2100,1800,40]);
  color("darkgreen")        translate([-400,-900,-300]) cube([210,1800,340]);  // bank, tops at +40
}

module full(){
  // pod axis along X, nose toward -X (upstream)
  translate([arm_end_x, 0, -pod_depth])
    rotate([0,-90,0]) wetpod_z();
  site();
}

mode = 0;
if (mode==0){ full(); river(); }
if (mode==1){ full(); }
if (mode==2){ wetpod_z(); }
if (mode==3){
  rotor_axis_z();
  translate([0,0,160]) rotorside_z();
  translate([0,0,300]) genpod_z();
  translate([0,0,540]) sensor_cage_z();
}
