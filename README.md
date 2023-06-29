# HIPIN API

## What does it do?

It's a simple script/container that will download the latest HIPIN version every night at 23:30 and serve the information of the executable as an API. This because the latest version is nowhere to be found on the internet and it might be handy for MSP's to have this information available for patch management.

## How to use

Download the repo as a .zip file and run ```docker build -t hipin-api .``` to create the image

To run the image just run ```docker run -d -p 8080:8080 --name hipin-api hipin-api:latest```

Port 8080 is the chosen port, if you want to run it on another port just change the first ```8080``` in the command above.