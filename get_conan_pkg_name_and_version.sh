#!/bin/bash

conan info . | awk -F'@' 'NR==1{print $1}'
