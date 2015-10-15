# Configuration
The configuration system of Vepybot is managed through the `config` module.
The commands are:
* `config list [<subsection>]`: List the categories and settings.
* `config get <setting>`: Return the value of a setting.
* `config reset <setting>`: Reset a setting to it's default.
* `config set <setting> <value>`: Change the value of a setting.
* `config add <setting> <value>`: Add a value to a list setting.
* `config remove <setting> <value>`: Remove a value from a list setting.

# Base Commands
## Help
* `help <command...>`: This will show you how to use a command and a short description of how to use it.
* `list`: This will list all modules currently loaded.
* `list <module>`: This will list commands from a module.
* `list *`: This will list all commands from all modules.
## More
* `more`: If a command goes over the character limit of the protocol, it will place the overflow in a `more` buffer and append a message to the output showing how many lines are in the buffer. The `more` command will return the next line in your more buffer.
* `more clear`: This will clear your `more` buffer.
## 
