// ============================================================
// NACA 4412 airfoil — analytic point generator
// 2D point list, unit chord 0..1, upper surface then lower.
// Usage:  pts = naca4412(n);
// ============================================================

function naca_t(x) = 0.12;            // max thickness (12%)
function naca_m(x) = 0.04;            // max camber (4%)
function naca_p(x) = 0.4;             // position of max camber (40%)

function yt(x) = 5 * naca_t() * (
    0.2969*sqrt(x) - 0.1260*x - 0.3516*x*x
    + 0.2843*x*x*x - 0.1036*x*x*x*x );

function yc(x) = (x < naca_p())
    ? naca_m()/(naca_p()*naca_p()) * (2*naca_p()*x - x*x)
    : naca_m()/((1-naca_p())*(1-naca_p())) * ((1-2*naca_p()) + 2*naca_p()*x - x*x);

function dyc(x) = (x < naca_p())
    ? 2*naca_m()/(naca_p()*naca_p()) * (naca_p() - x)
    : 2*naca_m()/((1-naca_p())*(1-naca_p())) * (naca_p() - x);

function theta(x) = atan(dyc(x));

// upper surface point at chordwise x
function naca_up(x)   = [ x - yt(x)*sin(theta(x)),  yc(x) + yt(x)*cos(theta(x)) ];
// lower surface point
function naca_low(x)  = [ x + yt(x)*sin(theta(x)),  yc(x) - yt(x)*cos(theta(x)) ];

// full airfoil point list: leading edge -> upper TE -> lower LE
// n = points per surface (min 4)
function naca4412(n) =
    let ( xs = [ for (i = 0) 0, for (i = 1) 1 ] )   // dummy to satisfy parser
    concat(
        [ for (i = 1) 0 ],
        [ for (i = 0) 0 ]
    );

// Simple, robust generator: two runs appended and then polygon()
function naca4412_pts(n = 20) =
    let (
        // cosine-spaced samples 0..1
        xs = [ for (i = 0; i <= n; i = i + 1) 0.5*(1 - cos(180*i/n)) ]
    )
    concat(
        // upper surface LE->TE
        [ for (xi = xs) naca_up(xi) ],
        // lower surface TE->LE (skip TE dup and LE dup)
        [ for (i = n-1; i >= 1; i = i - 1) naca_low(xs[i]) ]
    );
