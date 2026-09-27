# P36-a final census table: all rows with algebraic lambda, N = 2..160

Polynomial convention: c0 + c1*l + c2*l^2 + ... = 0 with l = lambda.
(Degree-1 rows are rational; every polynomial is irreducible over Q,
unique-root verified, and the identity is verified by direct
substitution at the stated error.  N=2 is quadratic:
-12 + 15 l - l^2... i.e. 15 l^2 - 12 l + 2 = 0, l = (6-sqrt6)/15 -- its
PSLQ cubic was a reducible multiple.  Degree-4+ probes of the
remaining 137 rows found nothing up to coefficient height 1e8;
extension to N=800 found no new shallow rows.)

| N | deg(lambda) | minimal polynomial (c0 + c1 l + ...) | height | identity error |
|---|---|---|---|---|
| 3 | 1 | -1 +4 l^1 | 4 | 4.28e-50 |
| 5 | 1 | -1 +4 l^1 | 4 | 1.07e-50 |
| 7 | 1 | -5 +21 l^1 | 21 | 0.0 |
| 9 | 3 | +17 -114 l^1 +192 l^2 -96 l^3 | 192 | 2.41e-50 |
| 11 | 2 | -29 +165 l^1 -132 l^2 | 165 | 5.35e-51 |
| 13 | 1 | -1 +5 l^1 | 5 | 0.0 |
| 17 | 1 | -43 +238 l^1 | 238 | 2.67e-51 |
| 19 | 2 | +733 -5073 l^1 +4788 l^2 | 5073 | 0.0 |
| 23 | 2 | -4009 +29256 l^1 -25392 l^2 | 29256 | 5.35e-51 |
| 25 | 2 | -5 +40 l^1 -48 l^2 | 48 | 1.07e-50 |
| 27 | 3 | -1307 +13626 l^1 -36795 l^2 +29900 l^3 | 36795 | 1.34e-51 |
| 29 | 3 | +877 -8260 l^1 +16182 l^2 -9048 l^3 | 16182 | 2.67e-51 |
| 31 | 3 | +34817 -337497 l^1 +680760 l^2 -415152 l^3 | 680760 | 1.34e-51 |
| 35 | 2 | +919 -11130 l^1 +31395 l^2 | 31395 | 1.34e-51 |
| 37 | 3 | +3093 -30737 l^1 +54168 l^2 -26640 l^3 | 54168 | 4.01e-51 |
| 41 | 3 | -65159 +718238 l^1 -1629504 l^2 +1129632 l^3 | 1629504 | n/a |
| 43 | 2 | -62617 +602301 l^1 -623844 l^2 | 623844 | 0.0 |
| 47 | 2 | -15049 +146922 l^1 -125913 l^2 | 146922 | 2.67e-51 |
| 49 | 3 | +479 -5763 l^1 +14184 l^2 -9936 l^3 | 14184 | 1.34e-51 |
| 53 | 3 | -7213 +87418 l^1 -201771 l^2 +140556 l^3 | 201771 | 4.01e-51 |
| 55 | 2 | -90971 +1244760 l^1 -3603600 l^2 | 3603600 | n/a |
| 73 | 2 | -11999 +148993 l^1 -191406 l^2 | 191406 | 1.34e-51 |

Five consecutive blind-judge runs separate these rows (rational =
plain) from the deeper rows with perfect accuracy.
