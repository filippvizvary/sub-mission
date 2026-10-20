// Coupling zone detail: rotor + carrier + wet cup + wall + dry cup, NO pod body.
use <probe.scad>
mode=98;
if (mode==98){
  translate([0,0,-30]) rotor_axis_z();
  translate([0,0,-30+hub_len/2+6]){
    rotorside_z();
    color("seagreen") translate([0,0,-magcup_gap]) cylinder(d=pod_od-4, h=magcup_gap);
    translate([0,0,-magcup_gap-magcup_h]) magcup_z();
    color("gray") translate([0,0,0]) cylinder(d=8,h=24);
  }
}
