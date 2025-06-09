from .constraint import Constraint

class AlwaysPassConstraint(Constraint):

    def introspect(self, backend_adapter, **kwargs):
        return {"message": "No constraint applied."}

    def evaluate(self, introspection_result) -> bool:
        return True
