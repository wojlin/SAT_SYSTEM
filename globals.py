import ast
import utlis

POS = ast.literal_eval(utlis.read_file('config/setup.json'))["ground_station"]
WIDTH = 180
HEIGHT = 45