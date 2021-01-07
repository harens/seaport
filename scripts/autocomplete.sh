#!/bin/bash

# See https://click.palletsprojects.com/en/7.x/bashcomplete/#activation-script

_SEAPORT_COMPLETE=source_bash seaport > ./seaport/commands/autocomplete/bash/seaport.sh
_SEAPORT_COMPLETE=source_zsh seaport > ./seaport/commands/autocomplete/zsh/seaport.sh
_SEAPORT_COMPLETE=source_fish seaport > ./seaport/commands/autocomplete/fish/seaport.sh
