"""intuition_pack: the contrast-exemplar-pack + mechanical-verifier plugin
(P138-tested, P139 architecture).

A Pack is the ATOMIC unit of distilled domain intuition:
  charter        single-evidence-source statement of the judgment rule
  exemplars      labeled contrast pairs (positive/near-boundary negative)
  verifier       name of a registered MECHANICAL verifier + its decision rule
  domain         routing key

Design rules carried from measurement:
  - the pack loads ATOMICALLY (P139: recall-fragments are not a pack)
  - ONE evidence source per judgment for weak models (P138: the
    verifier is EXECUTED here, never "read and weighed" by the model)
  - every judgment is logged with the verifier output attached
    (auditability is the product)
"""
from .pack import Pack, build_pack
from .store import get_store
from .verifiers import run_verifier, VERIFIERS
from .regression import mechanical_gate

__all__ = ["Pack", "build_pack", "get_store", "run_verifier", "VERIFIERS",
           "mechanical_gate"]
