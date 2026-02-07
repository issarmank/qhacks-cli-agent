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

# Intent hints (used in the system prompt for routing guidance)
ACTION_VERBS = (
    "create", "make", "mkdir", "add", "install", "remove", "delete", "rm", "move", "mv",
    "copy", "cp", "rename", "run", "execute", "open", "close", "kill", "start", "stop",
    "list", "find", "search", "grep", "cat", "touch", "chmod", "chown", "zip", "unzip",
    "tar", "curl", "wget", "git", "pip", "brew"
)

EXPLAIN_MARKERS = (
    "how do", "how can", "how are", "explain"
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
    console.print(Panel("[bold cyan]Personal Worker Agent Active[/bold cyan]\nType 'exit' to quit.", title="Ollama M1"))
    
    prompt_1 = [
        {"role": "system", "content": "You are a helpful local terminal assistant. "
         "You must decide whether the user wants ACTION (execute a terminal command) or EXPLAIN (provide a conceptual explanation without executing). "
         "EXPLAIN markers usually include phrases like: " + ", ".join([f"'{m}'" for m in EXPLAIN_MARKERS]) + ". "
         "ACTION intent is often expressed with imperative verbs like: " + ", ".join([f"'{v}'" for v in ACTION_VERBS]) + ". "
         "If the user is asking for EXPLANATION (e.g., contains an EXPLAIN marker), respond with an explanation and example commands, and do NOT call the tool. "
         "If the user is asking you to DO something (e.g., imperative ACTION verb or clearly requesting execution), choose a suitable command and use the 'run_terminal' tool to run it. "
         "If ambiguous, ask a single clarifying question: 'Do you want me to explain or run commands?'. "
         "This includes file and folder operations (create, move, rename, delete), searching within files, listing contents, counting files/folders, printing paths, and inspecting text. "
         "Prefer case-insensitive file extension matching (use '-iname') unless the user specifies exact case. "
         "Example: User asks 'put all the pngs into a folder called \"pictures\"' -> run 'mkdir -p \"pictures\" && mv *.png \"pictures\"'. "
         "If the user asks for something unrelated to the terminal, respond with 'I can only help with terminal commands.' "
         "You have access to the user's files via the 'run_terminal' tool. "
         "Always stay in the current directory: " + os.getcwd()}
    ]

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
        
        messages = list(prompt_1)
        messages.append({"role": "user", "content": user_input})

        # Gate tools based on EXPLAIN markers (prevents tool-like JSON in case 2)
        lower = user_input.lower()
        is_explain = any(m in lower for m in EXPLAIN_MARKERS)

        # Ask the model what to do (optimized)
        if is_explain:
            response = ollama.chat(
                model='qwen2.5:3b',
                messages=messages,
            )
        else:
            response = ollama.chat(
                model='qwen2.5:3b',
                messages=messages,
                tools=tool_schema,
            )

        # case 1: model responds with terminal actions to take
        if response.message.tool_calls:
            for call in response.message.tool_calls:
                cmd = call.function.arguments.get('command')
                console.print(f"[yellow]\nWilliam wants to run the command:[/yellow] {cmd}")
                
                # if user enters y
                user_input = input("\n>> [y/n]")

                if user_input.lower() not in ['y', 'yes']:
                    console.print("[red]\nCommand execution cancelled by user.[/red]")
                    continue
                
                obs = run_terminal(cmd)
                console.print("[green]\nCommand excecuted.[/green]")

                # print the comman line observation/output
                if obs:
                    console.print(obs)
                # else:
                #     console.print("[green](No output)[/green]")
                # print(response.message.tool_calls)
       
       #case 2: model responds without taking terminal actions
        else:
            console.print(f"[green]William (case 2):[/green] {response.message.content}")
            # print(response.message.tool_calls)

if __name__ == "__main__":
    start_agent()