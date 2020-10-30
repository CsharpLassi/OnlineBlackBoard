visibilities = ("creator_only", "public")

#  Global
default_draw_height = 256
default_draw_width = 1024

assert default_draw_width > 1, "default_draw_height must be greater than 1"
assert default_draw_width > 1, "default_draw_width must be greater than 1"

# Blackboard
default_blackboard_visibility = "creator_only"

assert (
    default_blackboard_visibility in visibilities
), "default_blackboard_visibility must be in visibilities"

# Lecture-Session
default_lecture_session_visibility = "public"

assert (
    default_lecture_session_visibility in visibilities
), "default_lecture_session_visibility must be in visibilities"
