import enum

def get_enum_as_dict(enum_class: enum.Enum):
    if not issubclass(enum_class, enum.Enum):
        raise ValueError("Input must be an Enum class.")

    enum_dict = {member.name: member.value for member in enum_class}
    return enum_dict

def get_enum_as_list(enum_class: enum.Enum):
    if not issubclass(enum_class, enum.Enum):
        raise ValueError("Input must be an Enum class.")

    enum_list = [member.value for member in enum_class]
    return enum_list