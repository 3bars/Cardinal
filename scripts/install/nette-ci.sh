#!/bin/bash

# Cardinal Continuous Integration using Nette
# falcon78921

# This script is designed to test the quality of the Cardinal PHP codebase. 

cd /var/www/html
/home/travis/.config/composer/nette/code-checker/code-checker -d /var/www/html
