# Yokkaichi Playground - Create lots of fake, Velocity-based Minecraft servers to scan

## Why?
- It might be useful for creating a Minecraft server scanner, so that you have many servers to scan safely without having to actually scan the internet
- You don't have to run a full, bloated Minecraft servers for testing

## Installation
You just have to run it like a normal Python script. Java 11+ is required of course, and you optionally might need to install `requests` package to get initial Velocity JAR, but you might as well avoid that by providing the JAR yourself with the name `velocity.jar`.

## Usage
- CLI way: `python playground.py START_IP END_IP PORTS`
- Interactive way: Run the script and answer the questions

## Important
- The IPs have to be in the loopback (127.0.0.0/8, or 127.0.0.0-127.255.255.255.254) range.
- Ports should be separated by commas. No spaces!
