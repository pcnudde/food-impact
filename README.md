# Food impact analysis

## Developer Documentation

This documentation explains how to set up this application in a new repository. The application allows users to upload CSV files for processing via GitHub Actions, with results sent via email.

## Architecture

1. **Frontend**: Static HTML/JS hosted on GitHub Pages
2. **Proxy**: Cloudflare Worker that securely forwards requests to GitHub API
3. **Processing**: GitHub Actions workflow that processes CSV files and emails results

## Setup Steps

1. **GitHub Repository Setup**:
   - Fork/clone this repository
   - Enable GitHub Pages for the frontend
   - Add repository secrets:
     - `MAIL_USERNAME`: Gmail address for sending results
     - `MAIL_PASSWORD`: Gmail app-specific password
     - `TOKEN_FOR_WORKER`: GitHub token with `repo` scope for the Cloudflare Worker
     - `CLOUDFLARE_API_TOKEN`: Token for deploying the worker

2. **Gmail Configuration**:
   - Use/create a Gmail account
   - Enable 2-factor authentication
   - Generate an App Password:
     1. Go to Google Account Settings > Security
     2. Under "2-Step Verification" > "App passwords"
     3. Generate new password for "Mail"
     4. Use this as `MAIL_PASSWORD` secret

3. **Cloudflare Setup**:
   - Create a Cloudflare account
   - Create an API token with Workers deployment permissions
   - Add as `CLOUDFLARE_API_TOKEN` secret in GitHub

4. **GitHub Token**:
   - Create a fine-grained personal access token:
     - Go to Settings > Developer settings > Personal access tokens
     - Grant `repo` scope access to your repository
   - Add as `TOKEN_FOR_WORKER` secret in GitHub

5. **Deploy**:
   - Push code to main branch
   - Worker will auto-deploy via GitHub Actions
   - Update `index.html` with your worker's URL (shown after first deployment)

## How it Works

1. User uploads CSV through the web interface (GitHub Pages)
2. Request goes to Cloudflare Worker
3. Worker securely forwards request to GitHub API
4. GitHub Actions workflow:
   - Processes the CSV
   - Emails results to user

## Security

- GitHub token is securely stored in Cloudflare Worker
- No sensitive tokens in frontend code
- Files processed in isolated GitHub Actions environment
- Results delivered only to specified email
- CORS headers ensure secure cross-origin requests

## Customization

To modify CSV processing logic, update the `process_csv()` function in `process_csv.py`.

## License

MIT
