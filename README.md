# IFTTTwebhooks
IFTTT script using the webhook makers channel to email subscribers about new entries to our Socrata open data portal

This is a script that will extract data from a json file and then process that data to email users about new events (records). With the records from yesterday the script will query the data and then process the data to create an email header and body. Lastly it will then post the formatted header and body to our IFTTT webhooks listener.

We ran into trouble using this script with our internal firewall. The hope is to eventually change this listener from our json file to the Socrata API.
