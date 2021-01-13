#!/usr/bin/env python3

# Script to generate a starting point for debconf in Ansible based on existing values in debconf
# Uses format from debconf-get-selections provided by debconf-utils
#
# sudo is needed to access passwords stored in debconf, consider converting those to variables backed by ansible vault
# Example command using only seen questions for postfix:
#   sudo debconf-get-selections | grep -Ff <(sudo debconf-show postfix | grep -F '*' |
#   cut -d " " -f 2 | tr -d ":") | ./debconf.py

import sys

def main():
    """Convert debconf-get-selections output on stdin to Ansible YAML debconf tasks on stdout"""
    contains_passwords = False
    contains_quotes = False
    for l in sys.stdin:
        w = l.rstrip("\n").split("\t", 4)
        # Two spaces indentation
        ind = "  "
        if len(w) == 4:
            print(f"- name: debconf {w[1]}")
            print(ind*1 + "debconf:" )
            print(ind*2 + f"name: {w[0]}")
            print(ind*2 + f"question: {w[1]}")
            print(ind*2 + f"vtype: {w[2]}")
            print(ind*2 + f"value: \'{w[3]}\'")
            # Don't log passwords
            if w[2] == "password":
                print(ind*1 + "no_log: True")
                contains_passwords = True
            # Warn if the value contains single quotes
            # Print value to make searching reasonable as output will contain a lot of single quotes
            if "'" in w[3]:
                print(f"Warning: Input contains single quotes which break quoting: {w[3]}", file=sys.stderr)
                contains_quotes = True
    if contains_passwords:
        print("Input contains passwords, consider converting those to variables backed by ansible vault",
            file=sys.stderr)
    if contains_quotes:
        print("Input contains single quotes which break quoting, please fix the generated YAML", file=sys.stderr)

if __name__ == '__main__':
    main()
