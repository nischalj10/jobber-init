# jobber

jobber is an agent designed to search and apply for jobs on your behalf. It is a high performant web agent with ability to browse and navigate websites.

### contributor installation

1. install poetry if not already installed
2. use python >=3.8 in venv
3. do poetry install

### run the agent

1. Start a chrome instance with this command and do necessary logins `sudo /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222`
2. use the command `python -u -m jobber.main`
3. example task for - `Task: Buy the book zero to one from amazon.in. Use COD and my default address.`
