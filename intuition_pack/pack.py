"""Pack model: the atomic payload of distilled intuition."""
import json
import time
from dataclasses import dataclass, field, asdict


@dataclass
class Exemplar:
    d: int                 # routing key of the example (domain-specific id)
    inputs: dict           # the stimulus fields the judge will see
    label: str             # the ground-truth verdict token
    note: str = ""         # why this exemplar is in the pack (contrast role)


@dataclass
class VerifierSpec:
    name: str              # key into verifiers.VERIFIERS
    rule: str              # human-readable decision rule
    executed_by: str = "agent"   # P138: verification is EXECUTED, never read-and-weighed


@dataclass
class Pack:
    domain: str
    charter: str           # single-evidence-source statement of the judgment rule
    exemplars: list        # list[Exemplar]
    verifier: VerifierSpec
    version: int = 1
    created_at: float = field(default_factory=time.time)
    source: str = ""       # provenance: which experiments distilled this pack
    triggers: list = field(default_factory=list)  # mechanical route keys

    def to_json(self) -> str:
        return json.dumps(asdict(self), indent=1)

    @classmethod
    def from_json(cls, s: str) -> "Pack":
        d = json.loads(s)
        d["exemplars"] = [Exemplar(**e) for e in d["exemplars"]]
        d["verifier"] = VerifierSpec(**d["verifier"])
        return cls(**d)

    def prompt_block(self) -> str:
        """The single-evidence-source judgment block (what condition B was
        in P138): charter + labeled exemplars, nothing else."""
        lines = [self.charter, "", "Calibration exemplars (exhaustively verified):"]
        for e in self.exemplars:
            parts = []
            for k, v in e.inputs.items():
                if isinstance(v, (list, dict)):
                    parts.append(f"{k}={json.dumps(v, ensure_ascii=False)}")
                else:
                    parts.append(f"{k}={v}")
            ins = ", ".join(parts)
            lines.append(f"  {ins}  -> {e.label}" + (f"   [{e.note}]" if e.note else ""))
        return "\n".join(lines)


def build_pack(domain: str, charter: str, exemplars: list, verifier: dict,
               source: str = "", triggers: list = None) -> Pack:
    default_triggers = [domain] + [t for t in domain.split("-")]
    return Pack(domain=domain, charter=charter,
                exemplars=[Exemplar(**e) for e in exemplars],
                verifier=VerifierSpec(**verifier), source=source,
                triggers=triggers or default_triggers)
