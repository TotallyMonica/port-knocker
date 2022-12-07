# Port Knocker

## Why does this even exist?

I found that my college has a port based firewall that blocks services without a reason why. This project was created to test what ports were and were not blocked so they could be used in email for Freedom of Information Acts.

## Usage

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
