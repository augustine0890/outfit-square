# Outfit Square
Outfit Square is a Python project designed for managing outfits and fashion choices. It integrates with MongoDB and provides functionality for organizing and categorizing clothing items.

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
- Add new packages to the project: `peotry add package-name`
- If you need to specify platform-specific dependencies (e.g., different packages for Linux and MacOS):
  - `poetry package-name --platform linux`

## Usage
1. Create a virtual environment (if not using Poetry): `python -m venv venv source venv/bin/activate  # On Windows: venv\Scripts\activate`
2. Run the application: `python main.py` --> It will default to loading the `prod.env`
   - Run your script with desired stage: `python main.py --stage dev`
3. Notes:
- Remember to replace `DISCORD_TOKEN`, and `MONGODB` with the actual environment variable names in `.env` files.

## Contributing
Contributions are welcome! If you find any issues or have suggestions, feel free to open an issue or submit a pull request.