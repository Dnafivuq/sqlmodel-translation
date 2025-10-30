# Run the app
    fastapi dev app.py

# Debug
If using vscode use this launch.json config to debug this test package.

{
    "name": "Debug FastAPI (like fastapi dev)",
    "type": "debugpy",
    "request": "launch",
    "module": "src.books_demo.app",
    "console": "integratedTerminal",
    "justMyCode": false,
}

This helps properly resolve package imports when debugging.