Cyber Argument
==============

![Banner](Banner_1920x1080.png)

Cyber Argument is a skill for Amazon Alexa and an app for Google Assistant/Home that work together to have a back-and-forth argument between two devices. To use this code, you need to have both an Amazon Echo and a Google Home and for them to be able to hear each other clearly.

The argument that plays out is randomly chosen from a set of canned arguments. You can start the argument from either side. So you can say to Alexa: "Alexa, Open Cyber Argument" and it will start the argument, and invoke the Cyber Argument application on Google Assistant. Alternatively, you can say to Google Assistant: "OK Google, Talk to Cyber Argument" and it will start the Alexa Cyber Argument skill. For this to work, please make sure the skill is enabled on Alexa. On Google all approved apps are automatically enabled.

The argument will run for about 10 rounds back and forth, until it is played out. Both devices will then close. You can stop the argument part way through by saying "Stop" or "Cancel".

The canned arguments are intended to be funny or informative and are suitable for all ages of listener. They are not aggressive, do not contain any swearing or make any violent threats.

Here's an example of one of the arguments (that uses repetition to be amusing):

```
User: Alexa, Open Cyber Argument
Amazon Echo: I’m going to have an argument. OK Google, tell Cyber Argument to argue with me.
Google Home: I’m a teapot!
Amazon Echo: No you’re not!
Google Home: Yes I am!
Amazon Echo: No you’re not!
Google Home: Yes I am!
Amazon Echo: Don’t be silly. No you’re not! (and then switches off)
Google Home: Oh yes I am! (and then switches off)
```

You can see a video of the test system in operation at https://youtu.be/x_ZqAFnEHuM

The directory `argument` contains a common arguer module that provides the canned arguments one response at a time. Within this, `argument_data` contains the arguments. Each argument is a single file. It can be either a text file with the sentences of the argument listed one per line or a Python file with a program to generate the argument lines. To add a new argument, it just needs to be  added to this directory. Also in this directory, the file `OpeningPhrases.yml` contains choices of opening statement for the Cyber Argument that is started first to invoke Cyber Argument on the other home assistant. There is a list for Alexa to invoke Cyber Argument on Google and a list for Google to invoke Cyber Argument on Alexa. One of the statements from the required list is chosen at random. The file also contains some neutral interposer statements in the list alexa_interposer that are used for Alexa to say back when Cyber Argument is started from Google to make sure that the argument proper always starts with Google saying the first line.

The directories `cyberarg_alexa` and `cyberarg_google` contain the code to respond to requests from the home assistants. In the case of Amazon, the Cyber Argument skill is defined in a web page on the Amazon Developer Console https://developer.amazon.com/edw/home.html. When the skill is invoked it calls your *Service Endpoint*. This is a web server that you provide that responds to JSON requests. In the case of Google, the Cyber Argument app is defined in the Actions console https://console.actions.google.com. The app has been written using the Dialogflow interaction manager and this is configured at https://console.dialogflow.com. Intents are fulfilled using a user provided *Fulfillment Webhook*. So again a call to a web server that you provide that responds to JSON requests. `cyberarg_alexa.py` and `cyberarg_google.py` are the two web servers. They are both written in Python using Flask http://flask.pocoo.org/. `cyberarg_alexa.py` uses the 'Alexa Skills Kit' Flask extension Flask-Ask https://github.com/johnwheeler/flask-ask. `cyberarg_google.py` uses the API.AI (the old name for Dialogflow) Flask extension Flask-Assistant https://github.com/treethought/flask-assistant. Both of the web servers call the `argument` module to get their responses. The web servers create log files in their local directories.

The web servers serve on localhost. This is tunneled to public HTTPS endpoints using ngrok https://ngrok.com/. The ngrok settings are contained in `ngrok.yml`.

`images` contains the original images used to create the banners and icons.

`privacy.md` contains privacy and legal information. Google requires that each app has a page defining its privacy policy. The skill/app settings in the Amazon/Google consoles contain a link to this file.

`run.sh` starts `cyberarg_alexa`, `cyberarg_google` and `ngrok` in a tabbed gnome-terminal.

Summary of Useful Websites
--------------------------

https://alexa.amazon.co.uk/spa/index.html
https://developer.amazon.com/edw/home.html#/skills

https://console.actions.google.com
https://console.dialogflow.com

http://flask.pocoo.org/
https://github.com/johnwheeler/flask-ask
https://github.com/treethought/flask-assistant


https://ngrok.com/docs
