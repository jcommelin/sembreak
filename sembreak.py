# Reformat a file according to semantic linebreaking.
# 
# Usage: echo <text> | sd sembreak

import argparse
import nltk
import sys

def semantic_break(text, max_line_length=80):
    sentences = nltk.sent_tokenize(text)
    for sentence in sentences:
        words = sentence.split()
        line = ''
        for word in words:
            if len(line) + len(word) + 1 > max_line_length:
                if ',' in line:
                    # Find the last comma in the line
                    last_comma_index = line.rindex(',')
                    # Yield the part of the line before the last comma
                    yield line[:last_comma_index+1]
                    # Start a new line with the part of the line after the last comma
                    line = line[last_comma_index+1:].lstrip() + ' ' + word
                else:
                    yield line
                    line = word
            else:
                line = line + ' ' + word if line else word
        yield line

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("max_line_length", type=int, nargs='?', default=80)
    args = parser.parse_args()

    text = sys.stdin.read()
    for line in semantic_break(text, args.max_line_length):
        print(line)

# TODO: add optional argument for line length (default 80)