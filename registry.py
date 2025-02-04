MODEL_REGISTRY = {}

def update_registry(new_entries):
    MODEL_REGISTRY.update(new_entries)

def get_registry():
    return MODEL_REGISTRY
