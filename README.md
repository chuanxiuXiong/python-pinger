# python-pinger

## Table of Contents
- [Introduction](#introduction)
- [Getting Started](#getting-started)
- [A Couple Things to Note](#a-couple-things-to-note)

## Introduction

This is a simple python implementation of pinger.

## Getting Started

1. Install [Python2]()
2. Install all the packages listed in packages.txt. If you have [pip](https://pypi.org/project/pip/) installed, you could run `pip install -r packages.txt` to install all the packages. If for some reason it does not work, please manually install all the libraries initialized at the beginning of pinger.py
3. To run the program:
    ```
        python pinger.py -d destinationIP -c count -l logFile -p payload
    ```

## A Couple Things To Note:
1. Since the grading does not include logfile, nothing will be written to the logfile that the user specifies.
2. Options are optional. Only when there are no options is there going to be an error message. DestinationIP is by default set to '8.8.8.8'. Count is by default set to '1'. Payload is by default set to 'hello'.
3. The program does not handle invalid options in the arguments of command line, which means count has to be an int and larger than 0, destinationIP has to be a valid IP seperated by dots. As the instruction suggests, the program does not look up the IP address in the DNS server, so the destinationIP cannot be a hostname. The program also assumes we use IPv4.
