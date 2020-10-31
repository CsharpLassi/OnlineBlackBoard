from obb.tools.enum import ExtendEnum


class Visibility(ExtendEnum):
    CREATOR_ONLY = "creator_only"
    PUBLIC = "public"


#  Global
default_draw_height = 256
default_draw_width = 1024

assert default_draw_width > 1, "default_draw_height must be greater than 1"
assert default_draw_width > 1, "default_draw_width must be greater than 1"

# Blackboard
default_blackboard_visibility = Visibility.PUBLIC.value

# Lecture-Session
default_lecture_session_visibility = Visibility.CREATOR_ONLY.value
