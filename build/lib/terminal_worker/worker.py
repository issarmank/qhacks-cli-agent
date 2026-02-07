import ollama
import subprocess
import os
from rich.console import Console
from rich.panel import Panel

# ollama pull qwen2.5:3b
# pip install ollama rich

#inside terminal_worker folder: pip install -e .
# 'worker'
console = Console()

# these phrases indicate the user wants an explanation rather than an action
EXPLAIN_MARKERS = (
    "how can i", "how do i", "why does", "explain"
)

# run_terminal is the tool that the llama model uses to interact with the terminal. It executes a bash command and returns the output.
def run_terminal(command: str):
    """Executes a bash command and returns the output."""
    try:
        # We use shell=True to allow complex commands
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.stdout:
            return result.stdout.rstrip("\n")
        if result.stderr:
            return result.stderr.rstrip("\n")
        return ""
    except Exception as e:
        return f"Error: {str(e)}"

# main agent function. Maintains conversation history and handles interactions with the model. 
# The model can choose to call the run_terminal tool to execute commands.
# it chooses to run_terminal by including a tool_calls field in its response, which specifies the command to run.
def start_agent():
    console.print(Panel("[bold cyan]Turtle Active[/bold cyan]\nType 'exit' to quit.", title="Ollama M1"))

    action_prompt = [{
        "role": "system", "content": "You are a helpful local terminal assistant. "
        "your response MUST include a tool_calls field with the 'run_terminal' tool to execute a terminal command. "
        "use the 'run_terminal' tool to run a suitable command for the user's request. "
        "This includes file and folder operations (create, move, rename, delete), searching within files, listing contents, counting files/folders, printing paths, and inspecting text. "
        "Prefer case-insensitive file extension matching (use '-iname') unless the user specifies exact case. "
        "Example: User asks 'put all the X formatted files into a folder called \"pictures\"' -> run 'mkdir -p \"pictures\" && mv *.X \"pictures\"'. "
        "If the user asks for something unrelated to the terminal, respond with 'I can only help with terminal commands.' "
        "You have access to the user's files via the 'run_terminal' tool. "
        "Always stay in the current directory: " + os.getcwd()
    }]

    explain_prompt = [{
        "role": "system", "content": "You are a helpful local terminal assistant. "
        "Provide explanations and example commands for the user's conceptual questions about terminal operations. "
        "Do NOT execute any commands. "
        "If the user asks for something unrelated to the terminal, respond with 'I can only help with terminal commands.' "
    }]

    # Define a strict tool schema (improves consistent structured tool_calls)
    tool_schema = [
        {
            "type": "function",
            "function": {
                "name": "run_terminal",
                "description": "Run a bash command and return its output.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute, e.g. 'pwd', 'ls -la', 'cat file.txt'"
                        }
                    },
                    "required": ["command"]
                },
            },
        }
    ]

    # continuously get user input and interact with the model
    while True:
        user_input = input("\n>> ")
        if user_input.lower() in ['exit', 'quit']: break

        # Gate tools based on EXPLAIN markers
        lower = user_input.lower()
        is_explain = any(m in lower for m in EXPLAIN_MARKERS)

        # EXPLAIN: model provides explanation without tool call
        if is_explain:
            explain_messages = list(explain_prompt)  # reset to explain prompt each time
            explain_messages.append({"role": "user", "content": user_input})

            print ("EXPLAIN")

            response = ollama.chat(
                model='qwen2.5:3b',
                messages=explain_messages,
            )

        # ACTION: model can call the run_terminal tool to execute commands
        else:
            action_messages = list(action_prompt)  # reset to action prompt each time
            action_messages.append({"role": "user", "content": user_input})

            response = ollama.chat(
                model='qwen2.5:3b',
                messages=action_messages,
                tools=tool_schema,
            )

        # case 1: model responds with terminal actions to take (ACTION)
        if response.message.tool_calls:
            for call in response.message.tool_calls:
                cmd = call.function.arguments.get('command')
                console.print(f"[yellow]\nWilliam wants to run the command:[/yellow] {cmd}")
                
                # if user enters y
                user_input = input("\n>> [y/n]\n")

                if user_input.lower() not in ['y', 'yes']:
                    console.print("[red]\nCommand execution cancelled by user.[/red]")
                    continue
                
                obs = run_terminal(cmd)
                console.print("[green]\nCommand excecuted.[/green]")

                # print the comman line observation/output
                if obs:
                    console.print(obs) #obs is the output from the terminal after running the command
       
       #case 2: model responds without taking terminal actions (EXPLAIN)
        else:
            console.print(f"[green]William (case 2):[/green] {response.message.content}")

if __name__ == "__main__":
    start_agent()