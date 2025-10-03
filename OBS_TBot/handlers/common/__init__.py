# handlers/__init__.py
from ..reminder import on_startup_reg
from ..common_button import register_callback_handler
from .common import register_common_handler
from .startup import on_startup_common


async def on_startup(dp):
    await on_startup_common(dp)
    await on_startup_reg(dp)


# Также можно объединить регистрацию обработчиков
def register_all_handlers(dp):
    register_callback_handler(dp)
    register_common_handler(dp)
    # register_other_handlers(dp)
