#!/bin/bash

# Force StarTech USB sound card to use Line In after boot

amixer -c 0 sset 'PCM Capture Source' Line
amixer -c 0 sset Line cap
amixer -c 0 sset Line 85% cap
