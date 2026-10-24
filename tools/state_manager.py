# GLOBAL FLAGS
study_mode = False
gate_mode = False


# -------------------------- STUDY MODE --------------------------
def set_study_mode(on: bool):
    global study_mode
    study_mode = on

def is_study_mode() -> bool:
    return study_mode


# -------------------------- GATE MODE --------------------------
def set_gate_mode(on: bool):
    global gate_mode
    gate_mode = on

def is_gate_mode() -> bool:
    return gate_mode
