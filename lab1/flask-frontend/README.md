# Flask Frontend Project

This project is a simple web application built using the Flask framework. It provides a user interface for interacting with a backend service, allowing users to test several scenarios concerning our backend DataBase.

## Project Structure

```sh
flask-frontend
├── app
│   ├── static
│   │   └── styles.css
│   ├── templates
│   │   └── index.html
|   ├── Backend
|   |   └── Backend.py
│   ├── __init__.py
│   └── routes.py
├── requirements.txt
└── README.md
```

## Setup Instructions

1. **Enter the dictionary**:

   ```sh
   cd flask-frontend
   ```

2. **Create a virtual environment** (optional but recommended):

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the required dependencies**:

   ```sh
   pip install -r requirements.txt
   ```

4. **Run the application**:

   ```sh
   python ./demo.py
   ```

5. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000`.

## Usage

- The main page will display a centered title at the top.
- Below the title, there is a dropdown checklist for selecting scenarios.
- After making a selection, click the submit button to send the request to the backend.
- The returned data will be displayed in a table below.
- Click return to get back to the main page.

## Dependencies

- Flask
- Any other necessary libraries (as specified in `requirements.txt`).
