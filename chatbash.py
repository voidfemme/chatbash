#!/usr/bin/env python3
# WORKERS OF THE WORLD UNITE! ✊
from typing import Dict
from rich import box
from rich.console import Console
from rich.markdown import Markdown
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
        except:
            print("Error: Could not set API key")
            sys.exit(1)

    def chat_gpt(self, conversation):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=conversation, temperature=0
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

    def request_explanation(self, command: str) -> str:
        explanation_request = (
            f"give a concise explanation of the following bash command: {command}"
        )
        self.update_conversation({"role": "user", "content": explanation_request})
        explanation = self.chat_gpt(self.conversation)["content"]
        self.update_conversation({"role": "assistant", "content": explanation})
        console.print(explanation)

    def refine_prompt(self, user_feedback: str) -> str:
        refined_prompt = self.chat_gpt(self.conversation)["content"]
        self.update_conversation({"role": "assistant", "content": refined_prompt})
        return refined_prompt

    def verify_command(self, command: str) -> str:
        self.update_conversation(
            {
                "role": "user",
                "content": f"echo this command if correct, or echo a revised version if there are errors: {command}",
            }
        )
        corrected_command = self.chat_gpt(self.conversation["content"])
        self.update_conversation({"role": "user", "content": corrected_command})
        return corrected_command.strip()

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

    def process_gpt_response(self, content, instruction):
        try:
            response = openai.Edit.create(
                input=content,
                instruction=instruction,
                engine="text-davinci-edit-001",
                temperature=0,
            )
            return response["choices"][0]["text"]
        except Exception as e:
            console.print(e, style="red")
            sys.exit(1)

    def refine_prompt_with_chatbot(self, user_feedback):
        self.update_conversation({"role": "user", "content": user_feedback})

        refined_prompt = self.chat_gpt(self.conversation)["content"]
        self.update_conversation({"role": "assistant", "content": refined_prompt})
        return refined_prompt


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
        chat.update_conversation({"role": "assistant", "content": explanation})
        sys.exit(0)

    conversation = [
        {
            "role": "system",
            "content": "rewrite the statement as a bash command. Omit formatting and commentary.",
        },
        {"role": "user", "content": prompt},
    ]

    chat_gpt_response = chat.chat_gpt(conversation)["content"]
    chat.update_conversation({"role": "assistant", "content": chat_gpt_response})

    command = chat_gpt_response.strip()

    while True:
        console.print(
            "Careful! Bash commands are powerful... make sure you understand the prompt",
            style="red",
        )
        run_flag = input(
            "1. run? [(r)un/(q)uit/e(x)plain/(f)eedback/(e)dit/(p)rint conversation]: "
        )
        match run_flag:
            # exit and run the command
            case "r":
                try:
                    subprocess.run(command, shell=True, check=True)
                    exit(0)
                except subprocess.CalledProcessError as e:
                    print(f"Error executing the command: {e}")
                    exit(1)

            # explain the command
            case "x":
                chat.request_explanation(command)
            case "f":
                user_feedback = input("Feedback: ")
                refined_prompt = chat.refine_prompt_with_chatbot(user_feedback)
                chat.update_conversation(
                    {"role": "assistant", "content": refined_prompt}
                )
                command = chat.process_gpt_response(
                    refined_prompt,
                    "remove any formatting and leave the bash command by itself",
                )
                print(command)
            case "e":
                chat_gpt_response = get_prompt_input(chat_gpt_response)
                chat.update_conversation(
                    {"role": "assistant", "content": chat_gpt_response}
                )
                command = chat.process_gpt_response(
                    chat_gpt_response,
                    "remove any formatting and return the bash command by itself",
                )
                console.print(command, style="blue")
            case "p":
                chat.print_conversation()
            case _:
                sys.exit(0)


if __name__ == "__main__":
    main()
