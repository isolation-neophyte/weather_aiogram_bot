from aiogram import Router, types


router = Router()


@router.message()
async def trash_collector(message: types.Message):
    await message.delete()
