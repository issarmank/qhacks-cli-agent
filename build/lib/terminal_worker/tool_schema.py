# Define a strict tool schema (improves consistent structured tool_calls)
def get_tool_schema():

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

    return tool_schema
