from enum import Enum

class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    UNIVERSITY_ADMIN = "university_admin"
    STUDENT = "student"
