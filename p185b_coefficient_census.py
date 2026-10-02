"""P185-b: coefficient-meter census (see RESEARCH_PLAN P185-b). Results table:
d=11 (h=8, d%12=11): log10 = 4.98   | d=23 (h=8, d%12=11): 8.28
d=47 (h=8, d%12=11): 12.87         | d=83 (h=8, d%12=11): 17.89
generic plateau d=19,29,31,37,41,43,53,59,61,67,71,73,79: 22.0-23.2
six rows: 0 (d=3), 2.86 (d=5), 3.78 (d=7), 5.93 (d=13), 7.08 (d=17)
Negative controls: d=19 (h=8, generic!), d=43 (h=8, generic!), d=73 (h=8, generic!)
=> h, class-group structure (Z/4xZ/2 forced), and d%12 all fail to predict.
Method: p185_landing_structure.descent_test with adaptive maxcoeff growth.
"""
print(__doc__)
