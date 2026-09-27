-- native_decide / decidedEq route:
theorem t1 : ¬ ((43 : Rat) / 238 = (143 : Rat) / 238) := by
  native_decide
#eval ((43 : Rat) / 238 == (143 : Rat) / 238)  -- false, computable
