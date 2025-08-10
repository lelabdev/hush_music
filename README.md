# Hush.dev - Simple & Private File Sharing

Hush.dev is a lightweight, self-hostable file sharing web application built with Python and Flask. It provides a simple interface for uploading, downloading, and managing files and folders, with a focus on privacy and ease of use.

The application features two access levels (view-only and editor), both protected by separate passwords. A key feature is the ability to generate temporary sharing links that automatically expire after 48 hours, ensuring that your shared files don't remain accessible forever.

## Features

- **File & Folder Management:** Upload, download, and delete files and entire folders.
- **Dual Access Levels:**
  - **Editor Mode:** Full permissions to upload, delete, and manage content.
  - **View-Only Mode:** Can only view and download files.
- **Password Protection:** Secure access for both editor and viewer roles.
- **Temporary Sharing Links:** Generate links to files that automatically expire after 48 hours.
- **Simple Web Interface:** Clean and intuitive UI for easy file navigation.

## Tech Stack

- **Backend:** Python, Flask
- **Testing:** pytest

## Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

- Python 3.x
- pip

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/hush.dev.git
   cd hush.dev
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   _On Windows, use `.venv\Scripts\activate`_

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your environment:**
   Create a `.env` file in the root of the project and add the following variables. These are the passwords for the two access levels.

   ```env
   SECRET_KEY=your_super_secret_key
   VIEW_PASSWORD=your_view_password
   EDIT_PASSWORD=your_edit_password
   ```

## Running the Application

To run the application in development mode, use the following command:

```bash
  python app.py
```

The application will be available at `http://127.0.0.1:5000`.

## Running Tests

To ensure everything is working as expected, run the test suite:

```bash
pytest
```

## Project Structure

```
/
├── app.py              # Main Flask application factory
├── config.py           # Configuration loader (from .env)
├── requirements.txt    # Project dependencies
├── test_app.py         # Pytest test suite
├── wsgy.py             # WSGI entry point for production
├── routes/
│   └── main.py         # Core application routes and logic
├── templates/          # HTML templates
└── uploads/            # Default directory for uploaded files (add to .gitignore)
```

## Contributing

Contributions are welcome! If you have a suggestion or find a bug, please open an issue or submit a pull request.

## License

This project is open source and available under the [MIT License](LICENSE).
