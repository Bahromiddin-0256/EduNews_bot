from aiogram.fsm.state import StatesGroup, State


class RegistrationState(StatesGroup):
    language = State()
    full_name = State()
    contact_number = State()
    district = State()
    school = State()


class SettingsState(StatesGroup):
    main_settings = State()
    language = State()
    full_name = State()
    phone_number = State()
    district = State()
    school = State()


class NewPostState(StatesGroup):
    media_upload = State()
    title_input = State()
    description_input = State()
    confirmation = State()


class MyPostsState(StatesGroup):
    view = State()


class CommentState(StatesGroup):
    input_comment = State()


class AdminState(StatesGroup):
    input_broadcast_message = State()
    input_user_reply = State()
