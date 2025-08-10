# hush_music - Simple & Private File Sharing

hush_music is a lightweight, self-hostable file sharing web application built with Python and Flask. It provides a simple interface for uploading, downloading, and managing files and folders, with a focus on privacy and ease of use.

The application features two access levels (view-only and editor), both protected by separate passwords. A key feature is the ability to generate temporary sharing links that automatically expire after 48 hours, ensuring that your shared files don't remain accessible forever.

## Features

- **File & Folder Management:** Upload, download, and delete files and entire folders.
- **Dual Access Levels:**
  - **Editor Mode:** Full permissions to upload, delete, and manage content.
  - **View-Only Mode:** Can only view and download files.
- **Password Protection:** Secure access for both editor and viewer roles.
- **Temporary Sharing Links:** Generate links to files that automatically expire after 48 hours.
- **Simple Web Interface:** Clean and intuitive UI for easy file navigation.
- **Self-Contained:** No database required — everything runs on the filesystem.

## Tech Stack

- **Backend:** Python 3, Flask
- **Security:** Environment variables, secure session handling
- **Testing:** pytest
- **Templates:** Jinja2
- **Deployment:** WSGI-ready (via `wsgi.py`)

## Getting Started

Follow these instructions to get a local copy up and running for development and testing purposes.

### Prerequisites

- Python 3.x
- pip

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/lelabdev/hush_music.git
   cd hush_music
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   _On Windows: `.venv\Scripts\activate`_

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   Create a `.env` file in the root directory:

   ```env
   SECRET_KEY=your_strong_secret_key_here
   VIEW_PASSWORD=your_view_password
   EDIT_PASSWORD=your_edit_password
   ```

   > 🔐 Use a strong `SECRET_KEY` (e.g., generated with `openssl rand -hex 32`). Never commit this file.

   For reference, copy the example:

   ```bash
   cp .env.example .env
   ```

   _(If `.env.example` doesn't exist yet, create it from your `.env` template.)_

## Running the Application

Start the development server:

```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000`.

> ⚠️ Use only for development. For production, use a WSGI server (e.g., Gunicorn + Nginx).

## Running Tests

Ensure the codebase behaves as expected:

```bash
pytest
```

You can also run with coverage:

```bash
pytest --cov=.
```

## Project Structure

```
/
├── app.py              # Flask application factory
├── config.py           # Loads and validates environment variables
├── requirements.txt    # Python dependencies
├── test_app.py         # Pytest suite
├── wsgi.py             # WSGI entry point for production
├── routes/
│   └── main.py         # Core routes and business logic
├── templates/          # HTML templates (Jinja2)
├── uploads/            # Stored files (add to .gitignore)
├── .env.example        # Environment template (safe to commit)
└── .gitignore          # Includes .env, .venv, uploads/, __pycache__/
```

## Contributing

Contributions are welcome! If you have a suggestion, bug report, or feature idea:

- Open an **issue** to discuss.
- Fork the repo, create a feature branch, and submit a **pull request**.

Please keep changes focused and include tests when possible.

## License

This project is open source and available under the [MIT License](LICENSE).
