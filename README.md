# YouTube Summarizer Server

## Project Overview

This repository hosts the **Plugin Server** powering the [YouTube Summarizer Plugin](https://cloud.typingmind.com/plugins/p-01K2ZV673969YHSTSY6V22YDXK) for [TypingMind](https://typingmind.com/). Built with Python and FastAPI, it provides a robust and efficient backend for fetching and processing YouTube video transcripts.

**Important Deployment Note:**
Be aware that YouTube actively blocks IP addresses associated with cloud providers (e.g., Render.com, AWS, Google Cloud). This means direct deployment to such platforms may result in errors when attempting to fetch transcripts.

To reliably bypass these blocks, this server is specifically configured to integrate with **Webshare rotating residential proxies**. You will need to obtain Webshare credentials and set them as environment variables in your deployment environment. Detailed instructions on how to set up these proxies are provided in the [Proxy Configuration](#proxy-configuration) section below.

---

## Hosting the Server Locally

Follow these steps to set up and run the YouTube Summarizer Server on your local machine. This is ideal for development, testing, or personal use.

### Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.10 or newer (up to 3.13):** Download from [python.org](https://www.python.org/downloads/).
*   **Git:** Download from [git-scm.com](https://git-scm.com/downloads/).
*   **Poetry:** A dependency management tool for Python.

### Step 1: Clone the Repository

Open your terminal or command prompt and clone this repository to your local machine:
    
    git clone https://github.com/Btran1291/TypingMind-Youtube-Summarizer-Server.git
    cd TypingMind-Youtube-Summarizer-Server

### Step 2: Install Poetry

If you don't have Poetry installed, follow these instructions. If you already have it, skip to Step 3.

*   **On macOS / Linux:**
    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```
*   **On Windows (PowerShell):**
    ```powershell
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    ```
    After installation, you might need to close and reopen your terminal, or run the command provided by the installer to add Poetry to your system's `PATH` (e.g., `[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Users\YourUser\AppData\Roaming\Python\Scripts", "User")` on Windows).

    Verify the installation:

    ```bash
    poetry --version
    ```

### Step 3: Install Project Dependencies

Navigate to your project directory (if you're not already there) and let Poetry install all the necessary libraries:

    cd TypingMind-Youtube-Summarizer-Server # Only if you're not already in the directory
    poetry install
This command will create a dedicated virtual environment for your project and install all dependencies.

### Step 4: Run the FastAPI Server

Once dependencies are installed, you can start the server:

    poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
The server will start and be accessible at `http://127.0.0.1:8000`. You will see messages in your terminal indicating that Uvicorn is running.

### Step 5: Configure the Plugin in TypingMind (Local Access)

To use your locally running server with the TypingMind plugin:

1.  **Ensure your local server is running** (from Step 4).
2.  **Open TypingMind**.
3.  **Go to Plugins** -> **YouTube Summarizer Plugin** -> **Settings**.
4.  In the **"Plugin User Settings"** section, set the **"Plugin Server URL"** to:
    ```
    http://localhost:8000
    ```
    **Important Note:** This `http://localhost:8000` URL is only accessible from your local machine where the server is hosted.

---

## Ngrok Tunneling (Access from Other Devices)

If you want to access your locally running plugin server from other devices (e.g., your mobile phone, another computer on your network) or from a cloud-hosted application, you can use a tunneling service like [ngrok](https://ngrok.com/).

### Step 1: Install and Authenticate Ngrok

1.  **Download ngrok:** Visit [ngrok.com/download](https://ngrok.com/download) and download the executable for your operating system.
2.  **Unzip** the downloaded file and place the `ngrok` executable in a directory accessible from your terminal (e.g., your system's PATH).
3.  **Authenticate:** Sign up for a free ngrok account. After signing up, you'll receive an authtoken. In your terminal, run:
    ```bash
    ngrok config add-authtoken <YOUR_AUTHTOKEN>
    ```
    (Replace `<YOUR_AUTHTOKEN>` with your actual token).

### Step 2: Start the Ngrok Tunnel

While your FastAPI server is running locally (from Step 4 of "Hosting the Server Locally"), open a **new terminal or command prompt window** and run:

    ngrok http 8000
Ngrok will start and provide you with a public `https://` URL (e.g., `https://<random-id>.ngrok-free.app`). This URL tunnels internet traffic directly to your local server.

### Step 3: Configure the Plugin in TypingMind (Remote Access)

1.  **Copy the `https://` URL** provided by ngrok.
2.  **Open TypingMind**.
3.  **Go to Plugins** -> **YouTube Summarizer Plugin** -> **Settings**.
4.  In the **"Plugin User Settings"** section, set the **"Plugin Server URL"** to the ngrok `https://` URL you just copied.

**Important Considerations for Ngrok:**

*   **Temporary URLs:** Ngrok's free tier provides a new, random public URL every time you start the tunnel. You will need to update the "Plugin Server URL" in TypingMind each time you restart ngrok.
*   **Local Machine Dependency:** Your plugin server will only be accessible as long as your local computer is running, connected to the internet, and the ngrok tunnel is active. It is not a 24/7 hosting solution.

---

## Proxy Configuration

This server is designed to work with **Webshare rotating residential proxies** to bypass YouTube's IP blocking. You will need to obtain your Webshare credentials and set them as environment variables in your deployment environment.

### Step 1: Obtain Webshare Credentials

1.  **Sign up for Webshare:** Go to [Webshare.io](https://www.webshare.io/) and create an account.
2.  **Purchase a Residential Proxy Package:** **Crucially, ensure you purchase a "Residential" proxy package.** (Avoid "Proxy Server" or "Static Residential" IPs, as these are often blocked by YouTube).
3.  **Retrieve Credentials:** From your [Webshare Proxy Settings](https://dashboard.webshare.io/proxy/settings) dashboard, obtain your:
    *   **Proxy Username**
    *   **Proxy Password**

### Step 2: Set Proxy Environment Variables

These credentials must be set as environment variables in the environment where your server is deployed (e.g., Render.com, Docker, or your local machine if you were running the server directly without `poetry run` and wanted to test proxies locally).

*   **`WEBSHARE_PROXY_USERNAME`**: Your Webshare Proxy Username.
*   **`WEBSHARE_PROXY_PASSWORD`**: Your Webshare Proxy Password.
*   **(Optional) `WEBSHARE_IP_LOCATIONS`**: A comma-separated list of 2-letter country codes (e.g., `us,de,gb`) to filter proxy IPs by location for lower latency.

---

## Deployment on Render.com

This section guides you through deploying your YouTube Summarizer Server on [Render.com](https://render.com/), utilizing the Webshare proxy configuration.

### Why Webshare Proxies are Essential for Cloud Deployment

This server does **not** utilize the official YouTube Data API, which has strict quotas but bypasses IP blocking. Instead, it relies on the `youtube-transcript-api` library, which directly accesses YouTube's unofficial endpoints. When deployed on cloud platforms like Render.com, the server's IP address is easily identified as a data center, leading to YouTube blocking requests (resulting in fetching errors).

To ensure reliable transcript fetching from a cloud environment, **Webshare rotating residential proxies are mandatory**. These proxies route your requests through IP addresses from real ISPs, making them appear as legitimate user traffic and effectively bypassing YouTube's blocks.

### Prerequisites

*   **Render.com Account:** An active account on [Render.com](https://render.com/).
*   **GitHub Repository:** Your server's code is available publicly at `https://github.com/Btran1291/TypingMind-Youtube-Summarizer-Server/`.
*   **Webshare Credentials:** You have obtained your Webshare Proxy Username and Password (as per the [Proxy Configuration](#proxy-configuration) section).

### Step 1: Deploy Directly from GitHub

You can deploy this server directly from its public GitHub repository to Render.com without needing to fork it first.

1.  **Log in to Render Dashboard:** Go to [https://dashboard.render.com/](https://dashboard.render.com/) and log in.
2.  **Create New Web Service:** Click "New" (usually on the left sidebar) and select "Web Service".
3.  **Connect to GitHub:** Select "GitHub" as your Git provider.
4.  **Public Git Repository:** Choose the option to "Build and deploy from a public Git repository".
5.  **Paste Repository URL:** In the provided field, paste the URL of this repository:
    ```
    https://github.com/Btran1291/TypingMind-Youtube-Summarizer-Server/
    ```
6.  Click "Connect".

### Step 2: Configure Service Details

Fill in the service details as follows:

*   **Service Name:** Choose a unique, descriptive name (e.g., `youtube-summarizer-server`). This will be part of your public URL.
*   **Region:** Select a region close to your users for optimal performance.
*   **Branch:** `main`.
*   **Root Directory:** Leave blank.
*   **Runtime:** Render should auto-detect **`Docker`** due to your `Dockerfile`.
*   **Build Command:** Leave blank (handled by `Dockerfile`).
*   **Start Command:**
    ```bash
    poetry run uvicorn main:app --host 0.0.0.0 --port 8000
    ```
*   **Environment Variables:** This is where you set the proxy credentials for Render.
    *   Click "Add Environment Variable" and add the following:
        *   **Key:** `WEBSHARE_PROXY_USERNAME`
        *   **Value:** Your actual Webshare Proxy Username.
    *   Click "Add Environment Variable" again:
        *   **Key:** `WEBSHARE_PROXY_PASSWORD`
        *   **Value:** Your actual Webshare Proxy Password.
    *   *(Optional: If you want to filter proxy IPs by location for lower latency, add another variable):*
        *   **Key:** `WEBSHARE_IP_LOCATIONS`
        *   **Value:** A comma-separated list of 2-letter country codes (e.g., `us,de,gb`).
*   **Instance Type:** Select **`Free`** for testing. (Note: Free instances spin down after inactivity and may have slower cold starts).

### Step 3: Deploy the Service

1.  **Click "Create Web Service"**.

Render will now begin the deployment process. You can monitor the build and deploy logs directly in the Render dashboard. This process can take several minutes, especially the first time, as it builds the Docker image and installs all dependencies.

### Step 4: Verify Deployment and Get Your Public URL

1.  **Monitor Logs:** Once the deployment is complete, ensure the logs show your Uvicorn server starting successfully (e.g., `INFO: Uvicorn running on http://0.0.0.0:8000`).
2.  **Copy Public URL:** Render will provide a public URL for your deployed service (e.g., `https://your-service-name.onrender.com/`). Copy this URL.

### Step 5: Configure the Plugin in TypingMind (Deployed Server)

1.  **Open TypingMind**.
2.  **Go to Plugins** -> **YouTube Summarizer Plugin** -> **Settings**.
3.  In the **"Plugin User Settings"** section, locate the **"Plugin Server URL"** field.
4.  **Paste the Render.com URL** you copied in Step 4 (e.g., `https://your-service-name.onrender.com`). Ensure there is **no trailing slash** at the end.
5.  **Save Changes**.

Your YouTube Summarizer Plugin in TypingMind is now configured to use your deployed server with Webshare proxies.


