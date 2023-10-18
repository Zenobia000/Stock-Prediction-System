
import argparse
parser = argparse.ArgumentParser()

parser.add_argument('--a', default='0,1,2,3',
                    type=int,
                    required=True,
                    help='數字A')
parser.add_argument('--b', default='0,1,2,3',
                    type=int,
                    required=True,
                    help='數字B')

args = parser.parse_args()
a = args.a
b = args.b
def printsomething(a, b):
    print(a + b)


if __name__ == '__main__':
    printsomething(a, b)
