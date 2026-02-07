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
    
    base_messages = [
        {"role": "system", "content": "You are a helpful local terminal assistant. "
         "Rule: If the user asks 'how to' or for instructions, answer directly with the associated terminal command, but do not execute it yourself."
         "Rule: If the user asks for a current fact/value (e.g., today's date, current folder), use run_terminal."
         "You have access to the user's files via the 'run_terminal' tool. "
         "Always stay in the current directory: " + os.getcwd()}
    ]

    # continuously get user input and interact with the model
    while True:
        user_input = input("\n>> ")
        if user_input.lower() in ['exit', 'quit']: break
        
        messages = list(base_messages)
        messages.append({"role": "user", "content": user_input})

        # Ask the model what to do
        response = ollama.chat(
            model='qwen2.5:3b',
            messages=messages,
            tools=[run_terminal],
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

                if obs:
                    console.print(obs)
                    console.print("[green]\nCommand executed.[/green]")
                # else:
                #     console.print("[green](No output)[/green]")
                # print(response.message.tool_calls)
       
       #case 2: model responds without taking terminal actions
        else:
            console.print(f"[green]William (case 2):[/green] {response.message.content}")
            # print(response.message.tool_calls)

if __name__ == "__main__":
    start_agent()