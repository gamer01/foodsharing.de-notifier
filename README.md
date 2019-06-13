## What it does
This tool will login on your foodsharing page, check your firms for pickups with empty slots and send emails as a notification
### Features
- sends email notifications
- trys to send as little emails as possible (only send a mail if a empty slot moves into the configured time window)

## Installation
It is very useful to run this as a daily cron-job, such that emails are sent automatically

## Configuration:
### Two additional files need to be created
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

### Structure of the notification email
Modify `email.tmpl`. You can use `{varname}` variables and those variables need to exist in the `general.conf` file.

### Other settings
the rest of the configuration is done inside the `general.conf`
