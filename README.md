# Port Knocker

## Why does this even exist?

I found that my college has a port based firewall that blocks services without a reason why. This project was created to test what ports were and were not blocked so they could be used in email for Freedom of Information Acts.

## Usage

The client needs to be "behind the firewall" and the server "outside the firewall". Be aware of any potentially blocked ports going into the server's network, and be prepared to ignore these as their status is indeterminate (you'll need to find another way to do this - recommendation is to find another place to run a server that isn't behind a port blocker). 

Server:

```bash
python3 server.py [-g interface] [-t timeout] [-g [known good ports]]
```

Client:

```bash
python3 client.py -a address [-t timeout] [-g [known good ports]]
```

## To-Do

- [ ] Create control panel
- [X] ~~*Don't scan known good ports*~~ [2022-12-07]
- [ ] Enable communication between the client and the server through a known good port.
