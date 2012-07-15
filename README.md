A bot that monitors actions on Trello boards and pushes notifications to Hipchat in a specified room.

The best way to use this is to create an account on Trello for your bot, then get a key and never-expiring token to use the API. Set your keys and tokens to the following environment variables:

    export TRELLO_KEY=<your Trello key>
    export TRELLO_TOKEN=<your Trello token>
    export TRELLO_USERNAME=<your bot username>
    export HIPCHAT_TOKEN=<your Hipchat token>

* Add the bot to any board you want it to monitor
* The bot will monitor actions on the board and push notifications to Hipchat
* Configure which room the bot pushes to by creating a card with the name hipchat:`<hipchat room name>` and then archive it
* The bot checks this card every time to see where notifications should be sent.  To turn off notifications, you can delete this card, or remove the bot from the board.

The bot is also capable of some custom actions.  See the TrelloAction class for an example of monitoring for text links in a card comment that look like local file paths and replacing it with a file:// link.
