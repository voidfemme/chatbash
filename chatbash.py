#!/usr/bin/env python3
# WORKERS OF THE WORLD UNITE ✊
from typing import Dict
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import openai
import os
import re
import readline
import subprocess
import sys

console = Console()


class ChatHandler:
    def __init__(self) -> None:
        self.set_api_key()
        self.conversation = []

    def set_api_key(self):
        try:
            openai.api_key = os.environ["OPENAI_API_KEY"]
        except KeyError:
            print("Error: Could not set API key")
            sys.exit(1)

    def chat_gpt(self, conversation):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=conversation, temperature=0.1
            )
            content = response["choices"][0]["message"]["content"]
            return {"role": "assistant", "content": content}
        except Exception as e:
            console.print(e, style="red")
            sys.exit(1)

    def update_conversation(self, append: Dict = None) -> None:
        if append is not None:
            self.conversation.append(append)
            role = append["role"]
            content = append["content"]
            console.print(f"{role.capitalize()}: {content}", style="green")

    def extract_code_block(self, response: str) -> str:
        code_block_pattern = r"```(.+?)```"
        match = re.search(code_block_pattern, response, re.S)
        if match:
            return match.group(1).strip()
        else:
            return response.strip()

    def request_explanation(self, command: str) -> str:
        explanation_request = (
            f"give a concise explanation of the following bash command: {command}"
        )
        self.update_conversation({"role": "user", "content": explanation_request})
        explanation = self.chat_gpt(self.conversation)["content"]
        self.update_conversation({"role": "assistant", "content": explanation})

    def refine_prompt(self, user_feedback: str) -> str:
        refined_prompt = self.chat_gpt(self.conversation)["content"]
        self.update_conversation({"role": "assistant", "content": refined_prompt})
        return refined_prompt

    def verify_command(self, command: str) -> str:
        self.update_conversation(
            {
                "role": "user",
                "content": f"echo the command if correct, or revise if there are errors: {command}",
            }
        )
        corrected_command = self.chat_gpt(self.conversation)["content"]
        edited_command = get_prompt_input(corrected_command)
        self.update_conversation({"role": "user", "content": edited_command})
        return edited_command.strip()

    def print_conversation(self):
        conversation_text = Text("\n\nConversation so far:\n\n", style="bold")
        for message in self.conversation:
            role = message["role"]
            content = message["content"]
            message_style = "green" if role == "assistant" else "white"
            conversation_text.append(f"{role.capitalize()}: ", style=message_style)
            conversation_text.append(f"{content}\n", style=message_style)
        panel = Panel(conversation_text, box=box.ROUNDED, style="white on black")
        console.print(panel)


def get_prompt_input(prompt: str) -> str:
    escaped_prompt = re.escape(prompt)
    readline.set_startup_hook(lambda: readline.insert_text(prompt).replace("\\", ""))
    try:
        user_input = input("Write a command (q for quit): ")
        if user_input == "q":
            sys.exit(0)
        return user_input
    finally:
        readline.set_startup_hook()


def main():
    chat = ChatHandler()
    args = sys.argv[1:]
    quick_explain = False

    if "-q" in args:
        quick_explain = True
        args.remove("-q")

    prompt = " ".join(args)

    if prompt == "":
        if quick_explain:
            print("Error: No command provided for quick explanation.")
            sys.exit(1)
        else:
            prompt = input("Write a command: ")
            if prompt == "q":
                sys.exit(0)

    if quick_explain:
        explanation = chat.request_explanation(prompt)
        sys.exit(0)

    conversation = [
        {
            "role": "system",
            "content": "Your goal is to collaborate with the user to generate a bash command. Only respond with one bash command per reply",
        },
        {
            "role": "user",
            "content": f"given the following prompt, generate a bash command. do not use any formatting. Do not provide any commentary: {prompt}",
        },
    ]

    chat_gpt_response = chat.chat_gpt(conversation)["content"]
    chat.update_conversation({"role": "assistant", "content": chat_gpt_response})
    command = chat.extract_code_block(chat_gpt_response)

    while True:
        console.print(
            "Careful! Bash commands are powerful... make sure you understand the prompt",
            style="red",
        )
        console.print(f"Command: {command}", style="bold")
        run_flag = input(
            "1. run? [(r)un/(q)uit/e(x)plain/(f)eedback/(e)dit/(p)rint conversation]: "
        )
        match run_flag:
            case "r":
                try:
                    subprocess.run(command, shell=True, check=True)
                    sys.exit(0)
                except subprocess.CalledProcessError as e:
                    print(f"Error executing the command: {e}")
                    sys.exit(1)

            case "x":
                chat.request_explanation(command)
            case "f":
                user_feedback = input("Feedback: ")
                chat.update_conversation({"role": "user", "content": user_feedback})
                refined_prompt = chat.refine_prompt(user_feedback)
                command = chat.extract_code_block(refined_prompt)
            case "e":
                corrected_command = chat.verify_command(command)
                command = chat.extract_code_block(corrected_command)
                console.print(command, style="blue")
            case "p":
                chat.print_conversation()
            case "q":
                sys.exit(0)
            case "t":
                if chat.conversation:
                    chat.conversation.pop()
                chat_gpt_response = chat.chat_gpt(chat.conversation)["content"]
                chat.update_conversation(
                    {"role": "assistant", "content": chat_gpt_response}
                )
                command = chat.extract_code_block(chat_gpt_response)
            case _:
                continue


if __name__ == "__main__":
    main()
