import asyncio
import random

from loguru import logger

from src.model import prepare_data
import src.utils
from src.utils.output import show_dev_info, show_logo, show_menu
from src.utils.reader import read_xlsx_accounts
from src.utils.constants import ACCOUNTS_FILE, Account
import src.model
from src.utils.check_github_version import check_version


async def start():
    async def launch_wrapper(account):
        async with semaphore:
            await account_flow(account, config)

    show_logo()
    show_dev_info()

    try:
        await check_version("0xStarLabs", "StarLabs-Discord")
    except Exception as e:
        import traceback

        traceback.print_exc()
        logger.error(f"Failed to check version: {e}")
        logger.info("Continue with current version\n")

    print("")

    config = src.utils.get_config()

    task = show_menu(src.utils.constants.MAIN_MENU_OPTIONS)
    if task == "Exit":
        return

    config.DATA_FOR_TASKS = await prepare_data(config, task)

    config.TASK = task

    # Читаем аккаунты из XLSX
    all_accounts = read_xlsx_accounts(ACCOUNTS_FILE)

    # Определяем диапазон аккаунтов
    start_index = config.SETTINGS.ACCOUNTS_RANGE[0]
    end_index = config.SETTINGS.ACCOUNTS_RANGE[1]

    # Если оба 0, проверяем EXACT_ACCOUNTS_TO_USE
    if start_index == 0 and end_index == 0:
        if config.SETTINGS.EXACT_ACCOUNTS_TO_USE:
            # Фильтруем аккаунты по конкретным номерам
            accounts_to_process = [
                acc
                for acc in all_accounts
                if acc.index in config.SETTINGS.EXACT_ACCOUNTS_TO_USE
            ]
            logger.info(
                f"Using specific accounts: {config.SETTINGS.EXACT_ACCOUNTS_TO_USE}"
            )
        else:
            # Если список пустой, берем все аккаунты
            accounts_to_process = all_accounts
    else:
        # Фильтруем аккаунты по диапазону
        accounts_to_process = [
            acc for acc in all_accounts if start_index <= acc.index <= end_index
        ]

    if not accounts_to_process:
        logger.error("No accounts found in specified range")
        return

    # Проверяем наличие прокси
    if not any(account.proxy for account in accounts_to_process):
        logger.error("No proxies found in accounts data")
        return

    threads = config.SETTINGS.THREADS

    # Создаем список аккаунтов и перемешиваем его
    if config.SETTINGS.SHUFFLE_ACCOUNTS:
        shuffled_accounts = list(accounts_to_process)
        random.shuffle(shuffled_accounts)
    else:
        shuffled_accounts = accounts_to_process

    # If using single account mode, use only the first account
    if config.SETTINGS.USE_SINGLE_ACCOUNT and shuffled_accounts:
        shuffled_accounts = [shuffled_accounts[0]]
        logger.info(f"Using single account mode, only processing account {shuffled_accounts[0].index}")

    # Создаем строку с порядком аккаунтов
    account_order = " ".join(str(acc.index) for acc in shuffled_accounts)
    logger.info(
        f"Starting with accounts {min(acc.index for acc in accounts_to_process)} "
        f"to {max(acc.index for acc in accounts_to_process)}..."
    )
    logger.info(f"Accounts order: {account_order}")

    semaphore = asyncio.Semaphore(value=threads)
    
    # Если включен режим одного аккаунта, запускаем его в бесконечном цикле
    if config.SETTINGS.USE_SINGLE_ACCOUNT and shuffled_accounts:
        logger.info(f"Starting infinite loop for single account mode with account {shuffled_accounts[0].index}")
        single_account = shuffled_accounts[0]
        while True:
            try:
                await launch_wrapper(single_account)
                # Делаем небольшую паузу перед следующим циклом
                pause = random.randint(
                    config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[0],
                    config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[1],
                )
                logger.info(f"Single account cycle completed. Pausing for {pause} seconds before next cycle...")
                await asyncio.sleep(pause)
            except asyncio.CancelledError:
                logger.info("Task cancelled, stopping single account loop")
                break
            except Exception as e:
                logger.error(f"Error in single account loop: {e}")
                # Делаем паузу перед повторной попыткой в случае ошибки
                await asyncio.sleep(5)
    else:
        # Обычный режим для нескольких аккаунтов
        tasks = []
        for account in shuffled_accounts:
            tasks.append(asyncio.create_task(launch_wrapper(account)))
        await asyncio.gather(*tasks)


async def account_flow(account: Account, config: src.utils.config.Config):
    try:
        pause = random.randint(
            config.SETTINGS.RANDOM_INITIALIZATION_PAUSE[0],
            config.SETTINGS.RANDOM_INITIALIZATION_PAUSE[1],
        )
        logger.info(f"[{account.index}] Sleeping for {pause} seconds before start...")
        await asyncio.sleep(pause)

        instance = src.model.Start(account, config)

        await wrapper(instance.initialize, config)

        await wrapper(instance.flow, config)

        # Skip pause if we're using a single account
        if not config.SETTINGS.USE_SINGLE_ACCOUNT:
            pause = random.randint(
                config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[0],
                config.SETTINGS.RANDOM_PAUSE_BETWEEN_ACCOUNTS[1],
            )
            logger.info(f"Sleeping for {pause} seconds before next account...")
            await asyncio.sleep(pause)
        else:
            logger.info("Using single account mode, not waiting for next account.")

    except Exception as err:
        logger.error(f"{account.index} | Account flow failed: {err}")


async def wrapper(function, config: src.utils.config.Config, *args, **kwargs):
    attempts = config.SETTINGS.ATTEMPTS
    for attempt in range(attempts):
        result = await function(*args, **kwargs)
        if isinstance(result, tuple) and result and isinstance(result[0], bool):
            if result[0]:
                return result
        elif isinstance(result, bool):
            if result:
                return True

        if attempt < attempts - 1:  # Don't sleep after the last attempt
            pause = random.randint(
                config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[0],
                config.SETTINGS.PAUSE_BETWEEN_ATTEMPTS[1],
            )
            logger.info(
                f"Sleeping for {pause} seconds before next attempt {attempt+1}/{config.SETTINGS.ATTEMPTS}..."
            )
            await asyncio.sleep(pause)

    return result


def task_exists_in_config(task_name: str, tasks_list: list) -> bool:
    """Рекурсивно проверяет наличие задачи в списке задач, включая вложенные списки"""
    for task in tasks_list:
        if isinstance(task, list):
            if task_exists_in_config(task_name, task):
                return True
        elif task == task_name:
            return True
    return False
