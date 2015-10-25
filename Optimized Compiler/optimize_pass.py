from compress_add import *
from compress_boolean import *
from eliminate_unneeded_unaries import *
from check_ast_equality import *
from local_interpreter import *
from remove_dead_code import *



def optimize(ast):
	ast_old = compress_dead_code(compress_booleans(remove_unneeded_unaries(ast)))
	ast_new = []

	while True:
		ast_new = local_interpreter(compress_add(ast_old), {})
		if is_equal(ast_old, ast_new):
			break
		ast_old = ast_new
	return ast_new
