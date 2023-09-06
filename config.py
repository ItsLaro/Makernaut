import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--isProd", help="Production Mode", action='store_true')
args = parser.parse_args()

isProd = args.isProd
