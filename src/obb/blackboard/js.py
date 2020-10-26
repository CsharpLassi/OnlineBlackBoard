from flask_assets import Bundle
from ..ext import assets

js_blackboard = Bundle('js/socket.js')
assets.register('js_blackboard', js_blackboard)

js_blackboard_user = Bundle('js/socket.js',
                            'js/blackboard/admin_user_list.js',
                            # 'js/blackboard/room_settings.js',
                            'js/blackboard/markdown_editor.js',
                            # 'js/blackboard/canvas.js',
                            'js/blackboard/content.js')
assets.register('js_blackboard_user', js_blackboard_user)

js_blackboard_board = Bundle('js/socket.js',
                             # 'js/blackboard/canvas.js',
                             'js/blackboard/content.js')
assets.register('js_blackboard_board', js_blackboard_board)

js_blackboard_lecture = Bundle('js/socket.js',
                               # 'js/blackboard/canvas.js',
                               'js/blackboard/content.js')
assets.register('js_blackboard_lecture', js_blackboard_lecture)
