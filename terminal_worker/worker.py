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

def run_terminal(command: str):
    """Executes a bash command and returns the output."""
    try:
        # We use shell=True to allow complex commands like piping
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        return output if output.strip() else "Success (No output)"
    except Exception as e:
        return f"Error: {str(e)}"

def start_agent():
    console.print(Panel("[bold cyan]Personal Worker Agent Active[/bold cyan]\nType 'exit' to quit.", title="Ollama M1"))
    
    messages = [
        {"role": "system", "content": "You are a helpful local terminal assistant. "
         "You have access to the user's files via the 'run_terminal' tool. "
         "Always stay in the current directory: " + os.getcwd()}
    ]

    while True:
        user_input = input("\n>> ")
        if user_input.lower() in ['exit', 'quit']: break
        
        messages.append({"role": "user", "content": user_input})

        # Ask the Brain what to do
        response = ollama.chat(
            model='qwen2.5:3b',
            messages=messages,
            tools=[run_terminal],
        )

        # If the Brain wants to move its 'hands' (execute a command)
        if response.message.tool_calls:
            print ("here")
            for call in response.message.tool_calls:
                cmd = call.function.arguments.get('command')
                console.print(f"[yellow]Robot is running:[/yellow] {cmd}")
                
                obs = run_terminal(cmd)
                messages.append(response.message)
                messages.append({"role": "tool", "content": obs, "name": "run_terminal"})
                
                # Get the final answer after the action
                final = ollama.chat(model='qwen2.5:3b', messages=messages)
                console.print(f"[green]Robot:[/green] {final.message.content}")
                print(response.message.tool_calls)
        else:
            console.print(f"[green]Else Robot:[/green] {response.message.content}")
            print(response.message.tool_calls)

if __name__ == "__main__":
    start_agent()