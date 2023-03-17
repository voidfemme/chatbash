# Chatbash

Chatbash is a command-line utility that helps users understand and verify bash
commands by interacting with a powerful AI language model. Users can provide a
command, request an explanation, give feedback on the generated explanations,
and execute the command once they're confident in its correctness. Chatbash
leverages OpenAI's GPT-3.5-turbo to provide concise and accurate explanations.
(hopefully. This software is an early alpha still)

## Features

- Request explanations for Bash commands
- Refine explanations based on user feedback
- Verify the correctness of a command
- Print the conversation history
- Execute the verified command

## Prerequisites

- Unix-based system
- Python 3.6 or higher
- `rich` library for rich-text console output
- OpenAI Python library
- A valid OpenAI API key

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/voidfemme/chatbash.git
   cd chatbash
   ```
2. Install the required Python libraries:
   `pip install rich openai`
3. Run the installation script:
   ```
   sudo ./install.sh
   ```
