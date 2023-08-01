# Louis Login Backend

## Step 1: Install Python

Before installing Flask, we need to install Python on our Windows machine. Go to the official Python website and download the latest version of Python for Windows.

Once the download is complete, run the installer and follow the instructions to install Python on your system. During the installation process, make sure to select the option to add Python to your system path.

## Step 2: Install VS Code

Next, we’ll need to install Visual Studio Code (VS Code) on our system. Go to the official VS Code website and download the latest version of VS Code for Windows.

Once the download is complete, run the installer and follow the instructions to install VS Code on your system.

## Step 3: Create a Virtual Environment

After installing Python and VS Code, we’ll need to create a virtual environment for our Flask project. A virtual environment is a self-contained environment that allows us to install Python packages without affecting the global Python installation on our system.

To create a virtual environment, open a new terminal window in VS Code and navigate to the root directory of your project. Then, run the following command to create a new virtual environment:

```bash
python -m venv venv
```

This command will create a new virtual environment named ‘venv’ in the root directory of your project.

## Step 4: Activate the Virtual Environment

After creating the virtual environment, we need to activate it. To activate the virtual environment, run the following command in the terminal:

```bash
venv\Scripts\activate
```
This command will activate the virtual environment, and you’ll see the name of your virtual environment in the terminal prompt.

## Step 5: Install Flask

With the virtual environment activated, we can now install Flask using pip, the package manager for Python. To install Flask, run the following command in the terminal:

```bash
pip install flask
```
This command will download and install Flask and all its dependencies in your virtual environment.

## Step 6: Run the Flask Application

With the Flask application created, we can now run it using the following command:
```bash
flask run
```
This command will start the Flask development server, and you’ll be able to access your application by navigating to http://localhost:5000/ in your web browser.

## Step 7: Starting the application with debugging

In the VS Code editor, click on the "Run and Debug" icon on the left-hand side panel, or press Ctrl + Shift + D on your keyboard. This will open the "Run and Debug" panel in VS Code. Click on start Debugging.



