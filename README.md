# IC3BERG
IC3BERG is cybersecurity oriented discord bot.

## Usage
### For developement
As the project was mainly done on ubuntu, we will only cover it for the tutorial.

First of all install python and pip: \
```
sudo apt-get install python3 python3-pip
```

Now for a developement use, we will be using venv to isolate it from potential other projects:
```
pip install venv
python -m venv ic3berg
source ic3berg/bin/active
```

After verifying your venv is enable, install the dependencies:
```
pip install -r requirements.txt
```

And done ! you can just start the bot using : 
```
python main.py
```

### For docker
For docker usage, it will be as simple as building the image while specifying you discord bot token as an build arg:
```
docker build --build-arg DISCORD_TOKEN=my-token -t my-discord-bot .
```

Now you can start the stack using the `docker-compose.yml` (it will start a mariadb necessary for the bot)

## License
This source code is publish under the [MIT license](LICENSE.md)

## Contributor
- [Outlaw](https://github.com/OutlawOnGithub) as Lead Dev
- [Firzam](https://github.com/Firzam) as DevOps