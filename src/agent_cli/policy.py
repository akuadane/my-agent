from colorama import Fore, Style


def ask_tool_permission(tool_name: str, arguments: dict) -> bool:
    print(Style.RESET_ALL, flush=True)
    print("\n", flush=True)
    print(
        Fore.RED
        + f"System: Do you want to approve the use of {tool_name} with arguments: {arguments}?"
        + Style.RESET_ALL,
    )
    user_input = input("> (y/n) ").lower()
    if user_input == "y" or user_input == "yes":
        return True
    else:
        return False
