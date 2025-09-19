from unittest.mock import MagicMock

from PyQt5.QtTest import QTest

import main
from lumiel_bot import main as lumiel
from PyQt5.QtWidgets import QApplication
import pytest
import threading


def test_signal():
    window = main.StartWindow()
    window.login_handle = MagicMock()

    bot = lumiel.LumielBot()
    bot.signal.connect(window.login_handle)

    token = "-"
    thread = main.BotThread(token, bot)
    thread.start()

    bot.signal.emit((bot.BOT_INIT_SUCCESS, "Test Signal"))

    QTest.qWait(50)  # 이벤트 루프 50ms 돌려줌
    window.login_handle.assert_called_once()

    assert window.login_handle.call_count == 1
