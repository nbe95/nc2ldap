#!/bin/bash

# Run the LDAP server and our python exporter in parallel
/container/tool/run &
/nc-ldap/main.py &
wait
