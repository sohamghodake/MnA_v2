from typing import Dict, List, Any, Optional
from src.graph.schema import Assumption

class AssumptionRegistry:
    def __init__(self):
        self._assumptions: Dict[str, Assumption] = {}
        self._used_in: Dict[str, List[str]] = {} # assumption_id -> [model_names]

    def add_assumption(self, assumption: Assumption):
        self._assumptions[assumption.id] = assumption

    def get(self, assumption_id: str, model_name: str) -> Optional[Any]:
        """Retrieves assumption value and logs usage."""
        if assumption_id in self._assumptions:
            if assumption_id not in self._used_in:
                self._used_in[assumption_id] = []
            self._used_in[assumption_id].append(model_name)
            return self._assumptions[assumption_id].value
        return None

    def get_dependencies(self, model_name: str) -> List[Assumption]:
        """Returns all assumptions used by a specific model."""
        return [
            self._assumptions[a_id] 
            for a_id, models in self._used_in.items() 
            if model_name in models
        ]
