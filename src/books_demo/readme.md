# Run the app
    fastapi dev app.py

# Debug
If using vscode use this launch.json config to debug this test package.

{
    "name": "Debug FastAPI Dev",
    "type": "debugpy",
    "request": "launch",
    "module": "fastapi",
    "args": ["dev", "src/books_demo/app.py"],
    "justMyCode": false
}

This helps properly resolve package imports when debugging.