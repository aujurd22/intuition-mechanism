example (a b c : Rat) : (a - b) * c = a * c - b * c := by ring
example (a b c : Rat) : a + b - (c + b) = a - c := by ring
theorem uq {S₀ S₁ RHS l l' : Rat} (hS : S₀ ≠ 0)
    (h₁ : l * S₀ + S₁ = RHS) (h₂ : l' * S₀ + S₁ = RHS) : l = l' := by
  have h : l * S₀ = l' * S₀ := by
    apply sub_eq_zero.mp
    have key : l * S₀ - l' * S₀ = 0 := by
      have e : l * S₀ + S₁ - (l' * S₀ + S₁) = 0 := by
        rw [h₁, h₂]; ring
      have e2 : l * S₀ + S₁ - (l' * S₀ + S₁) = (l - l') * S₀ := by ring
      rw [e2]; exact e
      -- note: rw with h₁ h₂ inside `have e` already used them
    have : (l - l') * S₀ = l * S₀ - l' * S₀ := by ring
    rw [← this]; exact key
  exact mul_right_cancel₀ hS h
