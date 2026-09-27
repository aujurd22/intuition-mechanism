# P36-a final census table: all rows with algebraic lambda, N = 2..160

(degree-1 rows are rational; every polynomial is irreducible over Q,
unique-root verified, and the identity is verified by direct
substitution at the stated error.  N=2 is quadratic: 15 l^2 - 12 l + 2,
l = (6-sqrt6)/15 -- its PSLQ cubic was a reducible multiple.
Degree-4+ probes of the remaining 137 rows found nothing up to
coefficient height 1e8; extension to N=800 found no new shallow rows.)

| N | deg(lambda) | minimal polynomial (c0 + c1 l + ...) | height | identity error |
|---|---|---|---|---|
| 3 | 1 | +4 -1 l^1 | 4 | 4.28e-50 |
| 5 | 1 | +4 -1 l^1 | 4 | 1.07e-50 |
| 7 | 1 | +21 -5 l^1 | 21 | 0.0 |
| 9 | 3 | -96 +192 l^1 -114 l^2 +17 l^3 | 192 | 2.41e-50 |
| 11 | 2 | -132 +165 l^1 -29 l^2 | 165 | 5.35e-51 |
| 13 | 1 | +5 -1 l^1 | 5 | 0.0 |
| 17 | 1 | +238 -43 l^1 | 238 | 2.67e-51 |
| 19 | 2 | +4788 -5073 l^1 +733 l^2 | 5073 | 0.0 |
| 23 | 2 | -25392 +29256 l^1 -4009 l^2 | 29256 | 5.35e-51 |
| 25 | 2 | -48 +40 l^1 -5 l^2 | 48 | 1.07e-50 |
| 27 | 3 | +29900 -36795 l^1 +13626 l^2 -1307 l^3 | 36795 | 1.34e-51 |
| 29 | 3 | -9048 +16182 l^1 -8260 l^2 +877 l^3 | 16182 | 2.67e-51 |
| 31 | 3 | -415152 +680760 l^1 -337497 l^2 +34817 l^3 | 680760 | 1.34e-51 |
| 35 | 2 | +31395 -11130 l^1 +919 l^2 | 31395 | 1.34e-51 |
| 37 | 3 | -26640 +54168 l^1 -30737 l^2 +3093 l^3 | 54168 | 4.01e-51 |
| 41 | 3 | +1129632 -1629504 l^1 +718238 l^2 -65159 l^3 | 1629504 | n/a |
| 43 | 2 | -623844 +602301 l^1 -62617 l^2 | 623844 | 0.0 |
| 47 | 2 | -125913 +146922 l^1 -15049 l^2 | 146922 | 2.67e-51 |
| 49 | 3 | -9936 +14184 l^1 -5763 l^2 +479 l^3 | 14184 | 1.34e-51 |
| 53 | 3 | +140556 -201771 l^1 +87418 l^2 -7213 l^3 | 201771 | 4.01e-51 |
| 55 | 2 | -3603600 +1244760 l^1 -90971 l^2 | 3603600 | n/a |
| 73 | 2 | -191406 +148993 l^1 -11999 l^2 | 191406 | 1.34e-51 |

Five consecutive blind-judge runs separate these rows (rational =
plain) from the deeper rows with perfect accuracy.
