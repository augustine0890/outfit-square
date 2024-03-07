# Outfit Square
Outfit Square is a Python project designed for managing outfits and fashion choices. It integrates with MongoDB and provides functionality for organizing and categorizing clothing items.

**Add [Outfit_Square](https://discord.com/oauth2/authorize?client_id=1214115282684088331&permissions=8&scope=bot%20applications.commands) to your Server**

## Installation
1. Make sure you have Python 3.11 installed.
2. Install Poetry if you haven’t already.
3. Clone this repository:
```bash
git clone https://github.com/augustine0890/outfit-square
cd outfit-square
```
4. Install dependencies using Poetry: `poetry install`
5. Notes:
- Add new packages to the project: `poetry add <package-name>`
  - Remove a package: `poetry remove <package-name>`
  - Add the package as a development dependency: `poetry add --group dev <package-name>`
- If you need to specify platform-specific dependencies (e.g., different packages for Linux and MacOS):
  - `poetry <package-name> --platform linux`
- To update all packages in your project: `poetry update`
  - To update a specific package to its latest version: `poetry update <package-name>`

## Usage
1. Create a virtual environment (if not using Poetry): `python -m venv venv source venv/bin/activate  # On Windows: venv\Scripts\activate`
2. Run the application: `python main.py` --> It will default to loading the `prod.env`
   - Run your script with desired stage: `python main.py --stage dev`
3. Notes:
- Run the Application as production:
  - Execute permissions: `chmod +x start_app.sh`
  - Run the application as background: `./start_app.sh`
  - Check the application is running: `ps -p $(cat outfit-square.pid)`
    - Display live view of process's resource usage
      - `top -p $(cat outfit-square.pid)`
    - Display the CPU and memory usage:
      - `ps -p $(cat outfit-square.pid) -o %cpu,%mem,cmd`
      - If the %CPU is over 100% that are running on multiple cores.
- Remember to replace `DISCORD_TOKEN`, and `MONGO_URI` with the actual environment variable names in `.env` files.

## Contributing
Contributions are welcome! If you find any issues or have suggestions, feel free to open an issue or submit a pull request.