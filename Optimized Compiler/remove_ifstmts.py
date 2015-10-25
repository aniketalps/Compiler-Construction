

from compiler import *
from x86_ast import *
from explicate_ast import *


ELSE_LABEL = 0
END_LABEL = 1
LABEL_COUNT = 0
def make_label(name):
	global LABEL_COUNT
	label = "label_" + str(LABEL_COUNT)
	LABEL_COUNT += 1
	if name == "if":
		return ["else_" + label, "end_" + label]
	else:
		return ["while_" + label, "end_while_" + label]

def remove_structured_code(in_x86_asts):
	out_x86_asts = []
	for x86 in in_x86_asts:
		if isinstance(x86, IfStmt):
			label = make_label("if")
			out_x86_asts.append(Cmpl(Const(0), x86.test))
			out_x86_asts.append(JmpEqual(label[ELSE_LABEL]))
			out_x86_asts += remove_structured_code(x86.then)
			out_x86_asts.append(JmpTo(label[END_LABEL]))
			out_x86_asts.append(Label(label[ELSE_LABEL] + ":"))
			out_x86_asts += remove_structured_code(x86.else_)
			out_x86_asts.append(Label(label[END_LABEL] + ":"))
		elif isinstance(x86, x86Compare):
			if x86.ops[0] == "!=":
				label = make_label("if")
				out_x86_asts.append(Pushl(Name("%ebx")))
				out_x86_asts.append(Movl(x86.expr, Name("%ebx")))
				out_x86_asts.append(Cmpl(Name("%ebx"), x86.ops[1]))
				out_x86_asts.append(Popl(Name("%ebx")))
				out_x86_asts.append(JmpEqual(label[ELSE_LABEL]))
				out_x86_asts.append(Movl(Const(1), x86.name))
				out_x86_asts.append(JmpTo(label[END_LABEL]))
				out_x86_asts.append(Label(label[ELSE_LABEL] + ":"))
				out_x86_asts.append(Movl(Const(0), x86.name))
				out_x86_asts.append(Label(label[END_LABEL] + ":"))
			else:
				label = make_label("if")
				out_x86_asts.append(Pushl(Name("%ebx")))
				out_x86_asts.append(Movl(x86.expr, Name("%ebx")))
				out_x86_asts.append(Cmpl(Name("%ebx"), x86.ops[1]))
				out_x86_asts.append(Popl(Name("%ebx")))
				out_x86_asts.append(JmpEqual(label[ELSE_LABEL]))
				out_x86_asts.append(Movl(Const(0), x86.name))
				out_x86_asts.append(JmpTo(label[END_LABEL]))
				out_x86_asts.append(Label(label[ELSE_LABEL] + ":"))
				out_x86_asts.append(Movl(Const(1), x86.name))
				out_x86_asts.append(Label(label[END_LABEL] + ":"))
		elif isinstance(x86, While):
			label = make_label("while")
			out_x86_asts.append(Label(label[ELSE_LABEL] + ":"))
			out_x86_asts += remove_structured_code(x86.test[1])
			out_x86_asts.append(Cmpl(Const(0), x86.test[0]))
			out_x86_asts.append(JmpEqual(label[END_LABEL]))
			out_x86_asts += remove_structured_code(x86.body)
			out_x86_asts.append(JmpTo(label[ELSE_LABEL]))
			out_x86_asts.append(Label(label[END_LABEL] + ":"))
		else:
			out_x86_asts.append(x86)
	return out_x86_asts
