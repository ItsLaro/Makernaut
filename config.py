import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--isDev", help="Development Mode", action='store_true')
args = parser.parse_args()

isProd = not args.isDev
