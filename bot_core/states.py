# -*- coding: utf-8 -*-
# Created by Peter Emelin
# skype: piter979797
# mail: emelin.petr@otr.ru

from aiogram.dispatcher.filters.state import State, StatesGroup

class My_profile(StatesGroup):
    """
        События в рамках модуля 'Мой профиль'
    """
    del_profile = State()

class Broadcast(StatesGroup):
    """
        События в рамках модуля 'Рассылка'
    """
    wait_accept = State()

class Feedback(StatesGroup):
    """
        События в рамках модуля 'Обратная связь'
    """
    wait_message = State()
    wait_answer = State()

class Processing_create_issue(StatesGroup):
    """
        События в рамках модуля 'создать заявку'
    """
    wait_project = State()
    wait_subject = State()
    wait_desc = State()
    wait_accept = State()

class Processing_issue_comment(StatesGroup):
    """
        События в рамках модуля 'оперция по заявкам'
    """
    wait_comment = State()
    wait_give_info = State()
    wait_reopen = State()


class Find_issue(StatesGroup):
    """
         События в рамках модуля 'поиска заявок по номеру'

    """
    enter_issue = State()

class Send_admin_message(StatesGroup):
    """
        События в рамках модуля отправки сообщения пользователям от администратора

    """
    wait_send = State()

class Register_process(StatesGroup):
    """
        Регистрация состояний в рамках модуля регистрации
    """
    wait_email = State()
    wait_code = State()
