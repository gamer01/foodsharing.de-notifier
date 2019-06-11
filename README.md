This tool will login on your foodsharing page, check your firms for pickups with empty slots and send emails as a notification

It is very useful to run this as a daily cron-job

The tool will create a json-file with the current pickups with empty slots, to prevent from sending emails when acutally not new information occured


## Two additional files need to be created
example emails.txt

    max.mustermann@mailbox.org
    dieter.horst@posteo.org

example credentials.conf

    [foodsharing.de]
    usr = <username for foodsharing.de>
    pwd = <password for foodsharing.de>

    [email]
    # used for the smtp authentication
    smtp_server   = <email host to send mails from e.g. "mailbox.org">
    smtp_username = <email username like "max.musterman">
    smtp_pwd      = <password for smtp login>

    # used for the email header
    sender_email  = <email like "max.mustermann@mailbox.org">
