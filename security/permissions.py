from security.guard import SecurityGuard

_guard = None


def get_security_guard():

    global _guard

    if _guard is None:

        _guard = SecurityGuard()

    return _guard

def default_user():

    return {
        "username": "employee",

        "sensitive_access": False,
    }


def authorize_request(
    user,
    question
):

    guard = get_security_guard()

    classification = guard.classify(
        question
    )

    decision = classification["decision"]

    if decision == "ALLOW":

        return {
            "allowed": True,
            "sensitive": False,
            "category": "normal",
            "reason": classification["reason"],
        }


    if decision == "DENY":

        # A real employee permission system will replace
        # this later.
        if user.get(
            "sensitive_access",
            False
        ):

            return {
                "allowed": True,
                "sensitive": True,
                "category": classification[
                    "category"
                ],
                "reason": classification[
                    "reason"
                ],
            }

        return {
            "allowed": False,
            "sensitive": True,
            "category": classification[
                "category"
            ],
            "reason": classification[
                "reason"
            ],
        }


    return {
        "allowed": False,
        "sensitive": True,
        "category": "uncertain",
        "reason": (
            "The security system could not safely "
            "determine whether this request is "
            "restricted."
        ),
    }