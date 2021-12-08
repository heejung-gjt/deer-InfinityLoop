from core.validation import code_validator

from charges.models  import Unit, DiscountOrPenalties


class DPMixin:
    def valid_code(self, type, code):
        if not code_validator(type, code):
            return {"error": True}
        
        return {"error": False}

    def valid_unit(self, type):
        if not Unit.objects.filter(name=type).exists():
            return {"error": True}
        
        return {"error": False}

    def create_dp(self, data, number, type):
        DiscountOrPenalties.objects.create(
                id         =data["code"],
                number     =number,
                description=data["description"],
                unit       =Unit.objects.get(name=data["unit"]),
                type_id    =type
            )
        return {"error": False}

