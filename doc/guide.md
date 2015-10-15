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

## Rights
Rights are flags like `admin` or `owner` that can be applied to an idstring.

You can also disable modules/commands or add ignoring to an idstring: `rights set irc:*!evilauth -*.echo.*` or `rights set irc:*!evilauth ignore`

An idstring is a protocol-specific string that is used to identify users, rooms, channels, or other entities that can have rights. See the protocol for it's idstring formats.

* `rights get -matches [<idstring>]`: Get the rights an idstring has, if the idstring is omitted it will return your rights and idstring. `-matches` will show the rights entries that were used to give the results.

In the `set` commands the idstring can also be a glob (`fnmatch`) that is matched against the actual idstring.
* `rights set <idstring> <right>`: Give a right to an idstring.
* `rights unset <idstring> <right>`: Take a right from an idstring.
